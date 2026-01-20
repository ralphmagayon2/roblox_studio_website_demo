# authentication/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, EmailVerification, PasswordResetToken, LoginAttempt, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_verified', 'is_under_13', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('display_name', 'date_of_birth', 'bio', 'avatar_url')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Safety', {'fields': ('is_under_13', 'parental_consent')}),
        ('OAuth', {'fields': ('google_id', 'discord_id')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_premium', 'robux_balance', 'friends_count', 'created_at')
    list_filter = ('is_premium', 'theme', 'language')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used', 'ip_address')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at')


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username_or_email', 'ip_address', 'success', 'attempted_at')
    list_filter = ('success', 'attempted_at')
    search_fields = ('username_or_email', 'ip_address')
    readonly_fields = ('attempted_at',)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'ip_address', 'is_active', 'last_activity')
    list_filter = ('is_active', 'device_type', 'created_at')
    search_fields = ('user__username', 'ip_address', 'session_key')
    readonly_fields = ('created_at', 'last_activity')