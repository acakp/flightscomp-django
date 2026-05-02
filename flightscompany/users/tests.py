from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_page_renders(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_success(self):
        response = self.client.post(reverse("users:login"), {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(int(self.client.session["_auth_user_id"]) == self.user.pk)

    def test_logout_success(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, reverse("index"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_registration_page_renders(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_registration_success(self):
        new_user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "NewPassword123!",
            "password2": "NewPassword123!",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post(reverse("users:register"), new_user_data)
        self.assertRedirects(response, reverse("users:register_done"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse("users:password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/password_reset_form.html")

    def test_profile_page_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, reverse("users:login") + "?next=" + reverse("profile"))

    def test_profile_page_renders_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
