from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"class": "form-input"})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-input"})
    )

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={"class": "form-input"}))
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"class": "form-input"}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует!")
        return email
