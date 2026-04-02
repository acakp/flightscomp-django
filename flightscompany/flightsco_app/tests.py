from django.db.models.deletion import ProtectedError
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
