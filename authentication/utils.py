# authentication/utils.py

import random
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

user = get_user_model()


def get_client_ip(request):
    """Get the client's IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get the user agent string from the request"""
    return request.META.get('HTTP_USER_AGENT', '')[:500]

# ============================
# OTP FUNCTIONS
# ============================

def generate_otp():
    """Generate a 6 digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def hash_otp(otp):
    """Hash OTP for secure storage"""
    return hashlib.sha256(otp.encode()).hexdigest()

def verify_otp(user, entered_otp):
    """Verify if entered OTP matches stored hash"""
    if not user.otp_code or not entered_otp:
        return False

    # Check if OTP has expired
    if user.otp_expires_at and timezone.now() > user.otp_expires_at:
        return False
    
    # Verify hash
    entered_hash = hash_otp(entered_otp)
    return user.otp_code == entered_hash

def send_otp_email(user, otp):
    """Send OTP code to user's email"""
    try:
        subject = 'Your Roblox Login Code'
        html_message = render_to_string('authentication/emails/otp_email.html', {
            'user': user,
            'otp': otp,
            'valid_minutes': 10,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"OTP email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
        return False

# ============================
# EMAIL VERIFICATIONS
# ============================

def send_verification_email(user, verification_token):
    """Send email verification link to user"""
    try:
        verification_url = f"{settings.SITE_URL}/auth/verify-email/{verification_token}/"

        subject = 'Welcome to Roblox - Verify Your Email'
        html_message = render_to_string('authentication/emails/verify_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False

# ============================
# PASSWORD RESET
# ============================  

def send_password_reset_email(user, reset_token):
    """Send password reset link to user"""
    try:
        reset_url = f"{settings.SITE_URL}/auth/reset-password/{reset_token}/"

        subject = 'Reset Your Roblox Password'
        html_message = render_to_string('authentication/emails/reset_password.html', {
            'user': user,
            'reset_url': reset_url,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False

# ============================
# RATE LIMITING
# ============================

def check_rate_limit(ip_address, username_or_email, limit=5, window_minutes=15):
    """
    Check if login attempts from this IP or for this user exceed the limit
    Returns (is_limited, attemts_count)
    """
    from .models import LoginAttempt

    cutoff_time = timezone.now() - timedelta(minutes=window_minutes)

    # Check IP-based attempts
    ip_attempts = LoginAttempt.objects.filter(
        ip_address=ip_address,
        attempted_at__gte=cutoff_time,
        success=False
    ).count()

    # Check user-based attempts
    user_attempts = LoginAttempt.objects.filter(
        username_or_email=username_or_email,
        attempted_at__gte=cutoff_time,
        success=False
    ).count()

    max_attempts = max(ip_attempts, user_attempts)

    return max_attempts >= limit, max_attempts


def log_login_attempt(username_or_email, ip_address, user_agent, success):
    """Log a login attempt for security tracking"""
    from .models import LoginAttempt

    try:
        LoginAttempt.objects.create(
            username_or_email=username_or_email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
    except Exception as e:
        logger.error(f"Failed to log login attempt: {str(e)}")

# ============================
# SESSION MANAGEMENT
# ============================

def create_user_session(request, user):
    """Create a tracked session for the user"""
    from .models import UserSession

    try:
        # Deactivate old sessions
        UserSession.objects.filter(user=user, is_active=True).update(is_active=False)

        # Create new session
        session = UserSession.objects.create(
            user=user,
            session_key=request.session.session_key,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            device_type=detect_device_type(request),
            is_active=True
        )

        logger.info(f"Created session for user {user.username}")
        return session
    except Exception as e:
        logger.error(f"Failed to create user session: {str(e)}")
        return None


def detect_device_type(request):
    """Detect device type from user agent"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        return 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        return 'tablet'
    else:
        return 'desktop'

# ============================
# INPUT SANITIZATION
# ============================

def sanitize_username(username):
    """Sanitize username input"""
    import re
    # Remove any characters that aren't alphanumeric or underscore
    return re.sub(r'[^a-zA-Z0-9_]', '', username.strip())


def sanitize_email(email):
    """Sanitize email input"""
    return email.strip().lower()