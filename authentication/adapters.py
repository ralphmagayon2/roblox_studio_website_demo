# # authentication/adapters.py
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from allauth.account.adapter import DefaultAccountAdapter
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     """Custom adapter to handle social account connections"""
    
#     def pre_social_login(self, request, sociallogin):
#         """
#         Invoked just after a user successfully authenticates via a social provider,
#         but before the login is actually processed.
#         We use it to connect existing users with social accounts.
#         """
#         # If user is already authenticated, link the account
#         if request.user.is_authenticated:
#             return
        
#         # Check if user exists with this email
#         try:
#             email = sociallogin.account.extra_data.get('email', '').lower()
#             if email:
#                 user = User.objects.get(email=email)
#                 sociallogin.connect(request, user)
#         except User.DoesNotExist:
#             pass
    
#     def populate_user(self, request, sociallogin, data):
#         """
#         Populate user instance with data from social provider
#         """
#         user = super().populate_user(request, sociallogin, data)
        
#         # Get provider data
#         provider = sociallogin.account.provider
#         extra_data = sociallogin.account.extra_data
        
#         # Set display name from social account
#         if provider == 'google':
#             user.display_name = extra_data.get('name', '')
#             user.avatar_url = extra_data.get('picture', '')
#             user.google_id = extra_data.get('id', '')
        
#         elif provider == 'discord':
#             username = extra_data.get('username', '')
#             discriminator = extra_data.get('discriminator', '')
#             user.display_name = f"{username}#{discriminator}" if discriminator else username
            
#             # Discord avatar URL
#             user_id = extra_data.get('id', '')
#             avatar_hash = extra_data.get('avatar', '')
#             if avatar_hash:
#                 user.avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
            
#             user.discord_id = user_id
        
#         # Mark as verified (since they authenticated via OAuth)
#         user.is_verified = True
        
#         return user


# class CustomAccountAdapter(DefaultAccountAdapter):
#     """Custom account adapter for additional user setup"""
    
#     def save_user(self, request, user, form, commit=True):
#         """
#         Save user with custom logic
#         """
#         user = super().save_user(request, user, form, commit=False)
        
#         # Additional setup
#         user.is_active = True
        
#         if commit:
#             user.save()
        
#         return user