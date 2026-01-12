from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path("join/", views.join, name="join"),
    path("games/", views.games, name="games"),
    path("create/", views.create, name="create"),
    path("robux/", views.robux, name="robux"),
    path("support/", views.support, name="support"),

    # Footer Section - About Us
    path("about_roblox/about/", views.about, name="about"),
    path("about_roblox/career/", views.career, name="career"),
    path("about_roblox/press/", views.press, name="press"),
    path("about_roblox/investors/", views.investors, name="investors"),

    # Footer Section - Help
    path("help/customer_support/", views.customer_support, name="customer_support"),
    path("help/safety_center/", views.safety, name="safety_center"),
    path("help/report_abuse/", views.report_abuse, name="report_abuse"),
    path("help/community_standards/", views.community_standards, name="community_standards"),

    # Footer Section - Resources
    path("resources/developer_hub/", views.developer_hub, name="developer_hub"),
    path("resources/education/", views.education, name="education"),
    path("resources/blog/", views.blog, name="blog"),
    path("resources/community/", views.community, name="community"),

    # Footer Section - Legal
    path("legal/term_of_use/", views.term_of_use, name="term_of_use"),
    path("legal/privacy_policy/", views.privacy_policy, name="privacy_policy"),
    path("legal/cookie_policy/", views.cookie_policy, name="cookie_policy"),
    path("legal/license/", views.license_view, name="license"),
]
