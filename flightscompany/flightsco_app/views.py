from django.shortcuts import render, redirect
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, "flightsco_app/index.html")


def auth(request):
    if request.method == "POST":
        # for now, just redirect to profile after form submission
        # real authentication will be implemented later
        return redirect("profile")
    return render(request, "flightsco_app/auth.html")


def profile(request):
    return render(request, "flightsco_app/profile.html")


def planes(request, plane_id):
    return HttpResponse(f"<h1>planes:</h1><p>{plane_id}</p>")
