from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html")

def crop_protection(request):
    return render(request, "crop-protection.html")

def seed(request):
    return render(request, "seeds.html")

def fertilizer(request):
    return render(request, "fertilizers.html")

def tools(request):
    return render(request, "tools.html")