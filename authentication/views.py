# authentication/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from datetime import timedelta
import logging

from .forms import SignupForm, LoginForm, PasswordResetRequestForm, PasswordResetConfirmationForm
from .models import EmailVerification, PasswordResetToken, LoginAttempt
from .utils import (
    send_verification_email, send_password_reset_email, send_otp_email,check_rate_limit, log_login_attempt, create_user_session, get_client_ip, get_user_agent, generate_otp, hash_otp, verify_otp, sanitize_username, sanitize_email
)

logger = logging.getLogger(__name__)
User = get_user_model()

# ============================
# SIGNUP VIEW
# ============================

@never_cache
@require_http_methods(["GET", "POST"])
def signup_view(request):
    """User registration view"""

    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('authentication:games')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            try:
                # Create User
                user = form.save()

                # Create email verification token
                verification = EmailVerification.objects.create(user=user)

                # Send verification email
                email_sent = send_verification_email(user, verification.token)

                if email_sent:
                    messages.success(
                        request,
                        f'Account created successfully! Please check {user.email} to verify your account.',
                        extra_tags='success'
                    )
                    logger.info(f"User registered: {user.username} ({user.email})")
                else:
                    messages.warning(
                        request,
                        'Account created but verification email failed to send. Please contact support.',
                        extra_tags='warning'
                    )
                    logger.warning(f"Failed to send verification email for {user.email}")

                return redirect('authentication:join')
            
            except Exception as e:
                logger.error(f"Signup error: {str(e)}")
                messages.error(
                    request,
                    'An error occurred during registration. Please try again.',
                    extra_tags='error'
                )
        else:
            # Form validation erros
            for field, errors, in form.errors.items():
                for error in errors:
                    messages.error(request, error, extra_tags='error')

    else:
        form = SignupForm()
    
    return render(request, 'authentication/auth.html', {'form': form})

# ============================
# EMAIL VERIFICATION
# ============================

@require_http_methods(["GET"])
def verify_email_view(request, token):
    """Verify user email with token"""

    try:
        verification = get_object_or_404(EmailVerification, token=token)

        if not verification.is_valid():
            messages.error(
                request,
                'This verification link has expired or already been used. Please request a new one.',
                extra_tags='error'
            )
            return redirect('authentication:join')
        
        # Verify the user
        user = verification.user
        user.is_verified = True
        user.save()

        # Mark verification as used
        verification.is_used = True
        verification.save()

        logger.info(f"Email verified for user: {user.username}")
        messages.success(
            request,
            'Email verified successfully! You can now log in.',
            extra_tags='success'
        )

        return redirect('authentication:join')

    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        messages.error(request, 'Invalid or expired verification link.', extra_tags='error')
        return redirect('authentication:join')

# ============================
# LOGIN VIEW (Step 1: Email + Password)
# ============================

@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view with rate limiting - Step 1: Verify credentials"""

    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('authentication:games')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)

            # Check rate limiting
            is_limited, attempt_count = check_rate_limit(ip_address, username_or_email)

            if is_limited:
                messages.error(
                    request,
                    'Too many failed login attempts. Please try again in 15 minutes.',
                    extra_tags='error'
                )

                logger.warning(f"Rate limit exceeded for {username_or_email} from {ip_address}")

                return render(request, 'authentication/auth.html', {'form': form})

            # Try to authenticate
            # Check if input is email or username
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    username = username_or_email
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)

            # Log the attempt
            log_login_attempt(username_or_email, ip_address, user_agent, success=user is not None)

            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Account is deactivated.', extra_tags='error')
                    return render(request, 'authentication/auth.html', {'form': form})
                
                if not user.is_verified:
                    messages.warning(
                        request,
                        'Please verify your email first. Check your inbox.',
                        extra_tags='warning'
                    )
                    return render(request, 'authentication/auth.html', {'form': form})

                # Generate and send OTP
                otp = generate_otp()
                user.otp_code = hash_otp(otp)
                user.otp_expires_at = timezone.now() + timedelta(minutes=10)
                user.save()

                # Send OTP email
                if send_otp_email(user, otp):
                    # Store user ID in session for OTP verification
                    request.session['otp_user_id'] = str(user.id)
                    request.session['remember_me'] = remember_me

                    messages.info(
                        request,
                        'Please enter the code send to your email.',
                        extra_tags='info'
                    )

                    return redirect('authentication:verify_otp')
                else:
                    messages.error(request, 'Failed to send verification code.', extra_tags='error')
            else:
                messages.error(request, 'Invalid username/email or password.', extra_tags='error')
        else:
            for field, errors in form.errors.item():
                for error in errors:
                    messages.error(request, error, extra_tags='error')
    else:
        form = LoginForm()

    return render(request, 'authentication/auth.html', {'form': form})

# ============================
# OTP VERIFICATION (STEP 2)
# ============================

@never_cache
@require_http_methods(["GET", "POST"])
def verify_otp_view(request):
    """OTP verification view - Step 2"""

    # Check if user came from login
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Please log in first.', extra_tags='error')
        return redirect('authentication:join')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid session.', extra_tags='error')
        return redirect('authentication:join')
    
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()

        if not otp:
            messages.error(request, 'Please enter the verification code.', extra_tags='error')
            return render(request, 'authentication/auth.html', {'user': user})
        
        # Verify OTP
        if verify_otp(user, otp):
            # Mark as OTP verified
            user.otp_verified = True
            user.otp_code = None # Clear OTP
            user.save()

            # Log user in
            login(request, user)

            # Create session tracking
            create_user_session(request, user)

            # Handle remember me
            remember_me = request.session.get('remember_me', False)
            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60) # 30 days
            else:
                request.session.set_expiry(0)

            # Clear session data
            request.session.pop('otp_user_id', None)
            request.session.pop('remember_me', None)

            logger.info(f"User logged in with 2FA: {user.username}")
            messages.success(request, f'Welcome back, {user.get_full_name}!', extra_tags='success')

            return redirect('authentication:games')
        else:
            # Check if expired
            if user.otp_expires_at and timezone.now() > user.otp_expires_at:
                messages.error(request, 'Verification code expired. Please request a new one.', extra_tags='error')
            else:
                messages.error(request, 'Invalid verification code.', extra_tags='error')
    
    return render(request, 'authentication/verify_otp.html', {'user': user})

# ============================
# EMAIL VERIFICATION
# ============================

@require_http_methods(["POST"])
def resend_otp_view(request):
    """Resend OTP code"""

    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Please log in first.', extra_tags='error')
        return redirect('authentication:join')
    
    try:
        user = User.objects.get(id=user_id)

        # Generate new OTP
        otp = generate_otp()
        user.otp_code = hash_otp(otp)
        user.otp_expires_at = timezone.now() + timedelta(minutes=10)
        user.save()

        # Send OTP
        if send_otp_email(user, otp):
            messages.success(request, 'New code sent to your email.', extra_tags='success')
        else:
            messages.error(request, 'Failed to send code.', extra_tags='error')
    
    except User.DoesNotExist:
        messages.error(request, 'Invalid session.', extra_tags='error')
        return redirect('authentication:join')
    
    return redirect('authentication:verify_otp')

# ============================
# PASSWORD RESET REQUEST
# ============================


@require_http_methods(["GET", "POST"])
def password_reset_request_view(request):
    """Request password reset"""

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            try:
                user = User.objects.get(email=email)

                # Invalidate old tokens
                PasswordResetToken.objects.filter(
                    user=user,
                    is_used=False
                ).update(is_used=True)

                # Create new reset token
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    ip_address=get_client_ip(request)
                )

                # Send reset email
                email_sent = send_password_reset_email(user, reset_token.token)

                if email_sent:
                    messages.success(
                        request,
                        'Password reset link sent! Check your email.',
                        extra_tags='success'
                    )
                    logger.info(f"Password reset requested for {user.email}")
                else:
                    messages.error(
                        request,
                        'Failed to send reset email. Please try again.',
                        extra_tags='error'
                    )
                
                return redirect('authentication:join')

            except User.DoesNotExist:
                # Don't reveal if email exists or not (security)
                messages.success(
                    request,
                    'If that email exists, a reset link has been sent.',
                    extra_tags='info'
                )
                return redirect('authentication:join')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error, extra_tags='error')

    else:
        form = PasswordResetRequestForm()

    return render(request, 'authentication/password_reset_request.html', {'form': form})

# ============================
# PASSWORD RESET CONFIRM
# ============================

@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request, token):
    """Confirm password reset with token"""

    try:
        reset_token = get_object_or_404(PasswordResetToken, token=token)

        if not reset_token.is_valid():
            messages.error(
                request,
                'This reset link has expired or already has been used.',
                extra_tags='error'
            )
            return redirect('authentication:password_reset_request')
        
        if request.method == 'POST':
            form = PasswordResetConfirmationForm(request.POST)

            if form.is_valid():
                password = form.cleaned_data.get('password')

                # Reset password
                user = reset_token.user
                user.set_password(password)
                user.save()

                # Mark token as used
                reset_token.is_used = True
                reset_token.save()

                logger.info(f"Password reset completed for {user.username}")
                messages.success(
                    request,
                    'Password reset successfully! You can now log in.',
                    extra_tags='success'
                )

                return redirect('authentication:join')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error, extra_tags='error')
            
        else:
            form = PasswordResetConfirmationForm()

        return render(request, 'authentication/password_reset_confirm.html', {'form': form})
    
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        messages.error(request, 'Invalid or expired reset link.', extra_tags='error')
        return redirect('authentication:password_reset_request')

# ============================
# LOGOUT
# ============================ 

@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """Log out user and clean session"""

    username = request.user.username

    # Deactivate user sessions
    from .models import UserSession
    UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).update(is_active=False)

    logout(request)

    logger.info(f"User logged out: {username}")
    messages.info(request, 'You have been logged out successfully!', extra_tags='info')

    return redirect('authentication:join')

# OAuth custom erros
def oauth_error(request):
    """Handle OAuth errors gracefully"""
    error = request.GET.get('error', 'Unknown error')
    messages.error(
        request,
        f'Authentication failed: {error}. Please try again or use email/password.',
        extra_tags='error'
    )

    return redirect('authentication:join')

# Create your views here.
def join(request):
    """Main authentication page with tab switching"""
    return render(request, 'authentication/auth.html')

def games(request):
    return render(request, 'authentication/games.html')

def create(request):
    return render(request, 'authentication/create.html')

def robux(request):
    return render(request, 'authentication/robux.html')

def support(request):
    return render(request, 'authentication/support.html')

# For About Roblox Section

def about(request):
    return render(request, 'authentication/about_roblox/about.html')

def career(request):
    return render(request, 'authentication/about_roblox/career.html')

def press(request):
    return render(request, 'authentication/about_roblox/press.html')

def investors(request):
    return render(request, 'authentication/about_roblox/investors.html')

# For Help section

def customer_support(request):
    return render(request, 'authentication/help/customer_support.html')

def safety(request):
    return render(request, 'authentication/help/safety.html')

def report_abuse(request):
    return render(request, 'authentication/help/report_abuse.html')

def community_standards(request):
    return render(request, 'authentication/help/community_standards.html')

# For Resources Section

def developer_hub(request):
    return render(request, 'authentication/resources/developer_hub.html')

def education(request):
    return render(request, 'authentication/resources/education.html')

def blog(request):
    return render(request, 'authentication/resources/blog.html')

def community(request):
    return render(request, 'authentication/resources/community.html')

# For Legal Section
def term_of_use(request):
    return render(request, 'authentication/legal/term_of_use.html')

def privacy_policy(request):
    return render(request, 'authentication/legal/privacy_policy.html')

def cookie_policy(request):
    return render(request, 'authentication/legal/cookie_policy.html')

def license_view(request):
    return render(request, 'authentication/legal/license.html')