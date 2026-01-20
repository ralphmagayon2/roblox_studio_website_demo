# authentication/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinLengthValidator
import uuid


class CustomUserManager(BaseUserManager):
    """Custom manager for User model"""
    
    def create_user(self, username, email, password=None, date_of_birth=None, **extra_fields):
        """Create and save a regular user"""
        if not username:
            raise ValueError('Users must have a username')
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            date_of_birth=date_of_birth,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for Roblox-style authentication"""
    
    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Authentication fields
    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text='Required. 3-20 characters. Letters, digits and underscores only.'
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='email address'
    )
    
    # Profile fields
    display_name = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Privacy & Safety
    is_under_13 = models.BooleanField(default=False)
    parental_consent = models.BooleanField(default=False)

    # OTP fields
    otp_code = models.CharField(max_length=255, blank=True, null=True) # Hashed OTP
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False) # Track if user has verified OTP before
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # OAuth fields
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    discord_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    # Fix for groups and permissions clash
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return self.display_name or self.username
    
    def get_short_name(self):
        return self.username
    
    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class UserProfile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Premium/Membership
    is_premium = models.BooleanField(default=False)
    premium_start_date = models.DateTimeField(blank=True, null=True)
    premium_end_date = models.DateTimeField(blank=True, null=True)
    
    # Virtual Currency
    robux_balance = models.PositiveIntegerField(default=0)
    
    # Privacy Settings
    PRIVACY_CHOICES = [
        ('everyone', 'Everyone'),
        ('friends', 'Friends Only'),
        ('no_one', 'No One'),
    ]
    
    who_can_message = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='everyone')
    who_can_join_game = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='everyone')
    show_online_status = models.BooleanField(default=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    theme = models.CharField(max_length=10, default='dark', choices=[('light', 'Light'), ('dark', 'Dark')])
    
    # Statistics
    total_games_created = models.PositiveIntegerField(default=0)
    total_visits = models.PositiveIntegerField(default=0)
    friends_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def is_premium_active(self):
        """Check if premium membership is currently active"""
        if self.is_premium and self.premium_end_date:
            return timezone.now() < self.premium_end_date
        return False


class EmailVerification(models.Model):
    """Email verification tokens"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification for {self.user.username}"
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def save(self, *args, **kwargs):
        """Set expiration to 24 hours from creation"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """Password reset tokens"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password Reset for {self.user.username}"
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def save(self, *args, **kwargs):
        """Set expiration to 1 hour from creation"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)


class LoginAttempt(models.Model):
    """Track login attempts for security"""
    
    username_or_email = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        db_table = 'login_attempts'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['ip_address', 'attempted_at']),
            models.Index(fields=['username_or_email', 'attempted_at']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} login attempt for {self.username_or_email}"


class UserSession(models.Model):
    """Track active user sessions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500)
    device_type = models.CharField(max_length=50, blank=True, null=True)  # mobile, desktop, tablet
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type} ({self.ip_address})"