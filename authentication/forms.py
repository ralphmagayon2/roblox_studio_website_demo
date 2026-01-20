# authentication/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .utils import sanitize_username, sanitize_email
import re

User = get_user_model()


class SignupForm(forms.ModelForm):
    """User registration form with validation"""

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password',
            'id': 'signup_password'
        }),
        label='Password',
        help_text='Minimum 8 characters with letters, numbers, and symbols'
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'id': 'signup_confirm_password'
        }),
        label='Confirm Password'
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'id': 'signup_dob'
        }),
        label='Date of Birth',
        required=False
    )

    agree_terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the Terms of Service'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'date_of_birth']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username',
                'id': 'signup_username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email',
                'id': 'signup_email'
            }),
        }

    def clean_username(self):
        """Validate username"""
        username = sanitize_username(self.cleaned_data.get('username', ''))

        if not username:
            raise ValidationError('Username is required')
        
        # Check length
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters')
        
        if len(username) > 20:
            raise ValidationError('Username must be less than 20 characters')

        # Check format (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can olny contain letters, numbers, and underscore')

        # Check if username exists
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already taken')
        
        return username.lower()

    def clean_email(self):
        """Validate email"""
        email = sanitize_email(self.cleaned_data.get('email', ''))

        if not email:
            raise ValidationError('Email is required')
        
        # Check if email exists
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('This email is already registered')
        
        return email.lower()
    
    def clean_date_of_birth(self):
        """Validate date of birth"""
        from datetime import date
        dob = self.cleaned_data.get('date_of_birth')

        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            if age < 13:
                # Set COPPA flag
                self.cleaned_data['is_under_13'] = True
            
            if age > 120:
                raise ValidationError('Please enter a valid date of birth')
        
        return dob

    def clean(self):
        """Validate password match and strength"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match')
            
            # Validate password strength using Django's validators
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
            
        return cleaned_data
    
    def save(self, commit=True):
        """Create user with hashed password"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = True
        user.is_verified = False

        # Set COPPA flag if user is under 13
        if self.cleaned_data.get('is_under_13'):
            user.is_under_13 = True
        
        if commit:
            user.save()

        return user
    

class LoginForm(forms.Form):
    """User login form"""

    username = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username or email',
            'id': 'login_username'
        }),
        label='Username or Email'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'id': 'login_password'
        }),
        label='Password'
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'id': 'rememberMe'
        })
    )

    def clean_username(self):
        """Sanitize username/email input"""
        value = self.cleaned_data.get('username', '').strip()

        if '@' in value:
            return sanitize_email(value)
        return sanitize_username(value.lower())
    

class PasswordResetRequestForm(forms.Form):
    """Request password reset form"""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        }),
        label='Email Address'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        # Check if email exists
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email addess')
        
        return email
    

class PasswordResetConfirmationForm(forms.Form):
    """Confirm password reset form"""

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create new password'
        }),
        label='New Password'
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm new password'
        }),
        label='Confirm Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Passwords do not match')
            
            # Validate password strength
            try:
                validate_password(password)
            except Exception as e:
                raise ValidationError(e.messages)
        
        return cleaned_data