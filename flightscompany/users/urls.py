from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView
)
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginUser.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterUser.as_view(), name="register"),
    path("register/done/", views.register_done, name="register_done"),
    path("manage/", views.manage_users, name="manage_users"),
    
    # Password Reset
    path("password-reset/", 
         PasswordResetView.as_view(
             template_name="users/password_reset_form.html",
             email_template_name="users/password_reset_email.html",
             success_url=reverse_lazy("users:password_reset_done")
         ), 
         name="password_reset"),
    path("password-reset/done/", 
         PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"), 
         name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/", 
         PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html",
             success_url=reverse_lazy("users:password_reset_complete")
         ), 
         name="password_reset_confirm"),
    path("password-reset/complete/", 
         PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), 
         name="password_reset_complete"),

    # Password Change
    path("password-change/", 
         PasswordChangeView.as_view(
             template_name="users/password_change_form.html",
             success_url=reverse_lazy("users:password_change_done")
         ), 
         name="password_change"),
    path("password-change/done/", 
         PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"), 
         name="password_change_done"),
]
