from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse

from .models import FlightArticle, FlightCategory, FlightTag


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

        self.assertEqual(
            article_admin.list_display,
            (
                "title",
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
        self.assertEqual(category_admin.prepopulated_fields, {"slug": ("name",)})
        self.assertEqual(tag_admin.prepopulated_fields, {"slug": ("name",)})

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
