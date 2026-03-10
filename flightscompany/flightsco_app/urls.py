from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("planes/<int:plane_id>/", views.planes, name="planes"),
]
