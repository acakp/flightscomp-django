from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("auth/", views.auth, name="auth"),
    path("profile/", views.profile, name="profile"),
    path("planes/<int:plane_id>/", views.planes, name="planes"),
]
