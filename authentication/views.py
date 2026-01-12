from django.shortcuts import render

# Create your views here.
def join(request):
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