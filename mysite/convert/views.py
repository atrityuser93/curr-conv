from django.shortcuts import render


# Create your views here.
def home(request):
    """use form on home page to get input and output currecies"""
    return render(request, template_name='/converter/home.html')