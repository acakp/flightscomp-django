from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import user_passes_test

from .forms import LoginUserForm, RegisterUserForm

User = get_user_model()

def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser_check)
def manage_users(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        if user_id and action in ["make_staff", "remove_staff"]:
            try:
                user_obj = User.objects.get(pk=user_id)
                if not user_obj.is_superuser: # Don't allow changing superuser staff status
                    user_obj.is_staff = (action == "make_staff")
                    user_obj.save()
            except User.DoesNotExist:
                pass
        return redirect("users:manage_users")

    users = User.objects.all().order_by("-is_superuser", "-is_staff", "username")
    context = {
        "title": "Управление пользователями",
        "users_list": users,
    }
    return render(request, "users/manage_users.html", context)

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "users/login.html"
    extra_context = {"title": "Авторизация"}

    def get_success_url(self):
        return reverse_lazy("index")

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    extra_context = {"title": "Регистрация"}
    success_url = reverse_lazy("users:register_done")

def register_done(request):
    return render(request, "users/register_done.html", {"title": "Регистрация завершена"})
