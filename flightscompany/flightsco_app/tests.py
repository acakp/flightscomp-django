import shutil
import tempfile
from io import BytesIO

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse
from django.test.utils import override_settings
from PIL import Image

from .models import FlightArticle, FlightCategory, FlightTag, UploadedFile


def create_test_image(name="test.jpg", color=(0, 102, 204)):
    buffer = BytesIO()
    image = Image.new("RGB", (40, 40), color)
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class FlightRelationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.domestic_category = FlightCategory.objects.create(
            name="Тестовые внутренние рейсы",
            slug="test-domestic-category",
        )
        cls.international_category = FlightCategory.objects.create(
            name="Тестовые международные рейсы",
            slug="test-international-category",
        )
        cls.family_tag = FlightTag.objects.create(
            name="Семейная поездка",
            slug="test-family-tag",
        )
        cls.weekend_tag = FlightTag.objects.create(
            name="Поездка на выходные",
            slug="test-weekend-tag",
        )

        cls.published_article = FlightArticle.objects.create(
            title="Тестовый опубликованный перелет",
            slug="test-published-flight",
            content="Подробное описание опубликованного тестового предложения.",
            route="Казань — Самара",
            price="9990.00",
            category=cls.domestic_category,
            status=FlightArticle.Status.PUBLISHED,
        )
        cls.published_article.tags.set([cls.family_tag, cls.weekend_tag])

        cls.other_published_article = FlightArticle.objects.create(
            title="Второй опубликованный перелет",
            slug="second-published-flight",
            content="Материал для проверки другой категории и тегов.",
            route="Казань — Стамбул",
            price="18990.00",
            category=cls.international_category,
            status=FlightArticle.Status.PUBLISHED,
        )
        cls.other_published_article.tags.set([cls.weekend_tag])

        cls.draft_article = FlightArticle.objects.create(
            title="Черновик тестового перелета",
            slug="test-draft-flight",
            content="Черновик не должен попадать в пользовательские списки.",
            route="Казань — Самара",
            price="8990.00",
            category=cls.domestic_category,
            status=FlightArticle.Status.DRAFT,
        )
        cls.draft_article.tags.set([cls.family_tag])

    def test_category_get_absolute_url(self):
        self.assertEqual(
            self.domestic_category.get_absolute_url(),
            reverse(
                "category_detail",
                kwargs={"category_slug": self.domestic_category.slug},
            ),
        )

    def test_tag_get_absolute_url(self):
        self.assertEqual(
            self.family_tag.get_absolute_url(),
            reverse("tag_detail", kwargs={"tag_slug": self.family_tag.slug}),
        )

    def test_category_delete_is_protected_when_articles_exist(self):
        with self.assertRaises(ProtectedError):
            self.domestic_category.delete()

    def test_category_page_shows_only_published_articles_in_selected_category(self):
        response = self.client.get(
            reverse(
                "category_detail",
                kwargs={"category_slug": self.domestic_category.slug},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_article.title)
        self.assertNotContains(response, self.other_published_article.title)
        self.assertNotContains(response, self.draft_article.title)

    def test_tag_page_shows_only_published_articles_for_selected_tag(self):
        response = self.client.get(
            reverse("tag_detail", kwargs={"tag_slug": self.family_tag.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_article.title)
        self.assertNotContains(response, self.other_published_article.title)
        self.assertNotContains(response, self.draft_article.title)

    def test_article_detail_displays_related_category_and_tags(self):
        response = self.client.get(self.published_article.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.domestic_category.name)
        self.assertContains(response, self.family_tag.name)
        self.assertContains(response, self.weekend_tag.name)


class FlightFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media = tempfile.mkdtemp()
        cls.override = override_settings(MEDIA_ROOT=cls.temp_media)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls.temp_media, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.category = FlightCategory.objects.create(
            name="Форма: внутренние рейсы",
            slug="forms-domestic-category",
        )
        cls.tag = FlightTag.objects.create(
            name="Форма: семейный отдых",
            slug="forms-family-tag",
        )

    def test_search_page_uses_django_form_and_shows_valid_result(self):
        response = self.client.get(
            reverse("search"),
            {
                "origin": "Москва",
                "destination": "Сочи",
                "departure": "2026-05-01",
                "return_date": "2026-05-09",
                "passengers": "2",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Москва → Сочи")
        self.assertContains(response, "2")

    def test_add_offer_page_creates_article_with_uploaded_photo(self):
        response = self.client.post(
            reverse("add_offer"),
            {
                "title": "Тестовый рейс в сочи",
                "slug": "testovyy-reys-v-sochi",
                "content": "Описание нового предложения для проверки формы.",
                "route": "Казань — Сочи",
                "price": "15990.00",
                "status": FlightArticle.Status.PUBLISHED,
                "category": self.category.pk,
                "tags": [self.tag.pk],
                "photo": create_test_image(),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        article = FlightArticle.objects.get(slug="testovyy-reys-v-sochi")
        self.assertEqual(article.category, self.category)
        self.assertTrue(article.photo.name.startswith("photos/"))
        self.assertEqual(article.tags.count(), 1)

    def test_add_offer_form_shows_custom_validation_error(self):
        response = self.client.post(
            reverse("add_offer"),
            {
                "title": "Test flight title",
                "slug": "test-flight-title",
                "content": "Попытка отправить форму с неверным заголовком.",
                "route": "Казань — Сочи",
                "price": "15990.00",
                "status": FlightArticle.Status.PUBLISHED,
                "category": self.category.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Должны быть только русские символы, цифры, дефис и пробел.",
        )
        self.assertFalse(FlightArticle.objects.filter(slug="test-flight-title").exists())

    def test_about_upload_page_saves_file_via_model(self):
        upload = SimpleUploadedFile(
            "ticket.txt",
            b"flight ticket payload",
            content_type="text/plain",
        )

        response = self.client.post(reverse("about"), {"file": upload}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(UploadedFile.objects.count(), 1)
        self.assertContains(response, "uploads_model/")

    def test_index_and_detail_render_uploaded_offer_image(self):
        article = FlightArticle.objects.create(
            title="Тестовое предложение с фото",
            slug="test-offer-with-photo",
            content="Описание предложения с фотографией для шаблонов.",
            route="Казань — Минеральные Воды",
            price="18390.00",
            category=self.category,
            status=FlightArticle.Status.PUBLISHED,
            photo=create_test_image("offer-photo.jpg"),
        )

        index_response = self.client.get(reverse("index"))
        detail_response = self.client.get(article.get_absolute_url())

        self.assertContains(index_response, article.photo.url)
        self.assertContains(detail_response, article.photo.url)


class FlightAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.superuser = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )

        cls.domestic_category = FlightCategory.objects.create(
            name="Внутренние тестовые рейсы",
            slug="admin-domestic-category",
        )
        cls.international_category = FlightCategory.objects.create(
            name="Международные тестовые рейсы",
            slug="admin-international-category",
        )
        cls.tag = FlightTag.objects.create(
            name="Горящий тариф",
            slug="admin-hot-tag",
        )

        cls.tagged_article = FlightArticle.objects.create(
            title="Рейс с тегами",
            slug="admin-tagged-flight",
            content="Подробное описание предложения с тегами.",
            route="Казань — Санкт-Петербург",
            price="15490.00",
            category=cls.domestic_category,
            status=FlightArticle.Status.PUBLISHED,
        )
        cls.tagged_article.tags.add(cls.tag)

        cls.untagged_article = FlightArticle.objects.create(
            title="Рейс без тегов",
            slug="admin-untagged-flight",
            content="Материал для проверки пользовательского фильтра.",
            route="Казань — Самара",
            price="7490.00",
            category=cls.domestic_category,
            status=FlightArticle.Status.DRAFT,
        )

        cls.international_article = FlightArticle.objects.create(
            title="Тестовый международный маршрут",
            slug="admin-international-flight",
            content="Материал для проверки поиска по названию категории.",
            route="Казань — Стамбул",
            price="22490.00",
            category=cls.international_category,
            status=FlightArticle.Status.PUBLISHED,
        )

    def setUp(self):
        self.client.force_login(self.superuser)

    def test_admin_index_uses_custom_branding_and_styles(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Панель администрирования Flights Company")
        self.assertContains(response, "Управление каталогом авиапредложений")
        self.assertContains(response, static("flightsco_app/css/admin.css"))

    def test_models_are_registered_with_expected_admin_settings(self):
        article_admin = admin.site._registry[FlightArticle]
        category_admin = admin.site._registry[FlightCategory]
        tag_admin = admin.site._registry[FlightTag]
        upload_admin = admin.site._registry[UploadedFile]

        self.assertEqual(
            article_admin.list_display,
            (
                "title",
                "post_photo",
                "route",
                "price",
                "time_create",
                "status",
                "category",
                "brief_info",
            ),
        )
        self.assertEqual(article_admin.list_editable, ("status", "category"))
        self.assertEqual(article_admin.prepopulated_fields, {"slug": ("title",)})
        self.assertEqual(article_admin.filter_horizontal, ("tags",))
        self.assertEqual(article_admin.readonly_fields, ("post_photo", "time_create", "time_update"))
        self.assertEqual(category_admin.prepopulated_fields, {"slug": ("name",)})
        self.assertEqual(tag_admin.prepopulated_fields, {"slug": ("name",)})
        self.assertEqual(upload_admin.list_display, ("id", "file", "time_create"))

    def test_admin_search_finds_articles_by_related_category_name(self):
        response = self.client.get(
            reverse("admin:flightsco_app_flightarticle_changelist"),
            {"q": "Международные"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.international_article.title)
        self.assertNotContains(response, self.tagged_article.title)

    def test_admin_custom_filter_shows_only_articles_without_tags(self):
        response = self.client.get(
            reverse("admin:flightsco_app_flightarticle_changelist"),
            {"tag_state": "without_tags"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.untagged_article.title)
        self.assertNotContains(response, self.tagged_article.title)

    def test_admin_publish_action_updates_status_and_shows_message(self):
        response = self.client.post(
            reverse("admin:flightsco_app_flightarticle_changelist"),
            {
                "action": "set_published",
                "_selected_action": [str(self.untagged_article.pk)],
                "index": 0,
                "select_across": 0,
            },
            follow=True,
        )

        self.untagged_article.refresh_from_db()

        self.assertEqual(self.untagged_article.status, FlightArticle.Status.PUBLISHED)
        self.assertContains(response, "Изменено 1 записи(ей).")

    def test_admin_draft_action_updates_status_and_shows_warning_message(self):
        response = self.client.post(
            reverse("admin:flightsco_app_flightarticle_changelist"),
            {
                "action": "set_draft",
                "_selected_action": [str(self.tagged_article.pk)],
                "index": 0,
                "select_across": 0,
            },
            follow=True,
        )

        self.tagged_article.refresh_from_db()

        self.assertEqual(self.tagged_article.status, FlightArticle.Status.DRAFT)
        self.assertContains(response, "1 записи(ей) сняты с публикации!")
