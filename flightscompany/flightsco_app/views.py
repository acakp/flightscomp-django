from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("index INDEX INDEX index")


def planes(request, plane_id):
    return HttpResponse(f"<h1>planes:</h1><p>{plane_id}</p>")
