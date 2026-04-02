from django.db import models
from django.urls import reverse


class FlightCategory(models.Model):
    name = models.CharField(
        max_length=100, db_index=True, verbose_name="Название категории"
    )
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True, verbose_name="URL"
    )

    class Meta:
        verbose_name = "Категория перелетов"
        verbose_name_plural = "Категории перелетов"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"category_slug": self.slug})


class FlightTag(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Название тега")
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True, verbose_name="URL"
    )

    class Meta:
        verbose_name = "Тег предложения"
        verbose_name_plural = "Теги предложений"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tag_detail", kwargs={"tag_slug": self.slug})


class PublishedFlightManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=FlightArticle.Status.PUBLISHED)


class FlightArticle(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        PUBLISHED = 1, "Опубликовано"

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True, verbose_name="URL"
    )
    content = models.TextField(blank=True, verbose_name="Описание")
    route = models.CharField(max_length=255, verbose_name="Маршрут")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Стоимость"
    )
    category = models.ForeignKey(
        FlightCategory,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="Категория",
    )
    tags = models.ManyToManyField(
        FlightTag,
        blank=True,
        related_name="articles",
        verbose_name="Теги",
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Статус публикации",
    )

    objects = models.Manager()
    published = PublishedFlightManager()

    class Meta:
        verbose_name = "Предложение по перелету"
        verbose_name_plural = "Предложения по перелетам"
        ordering = ["-time_create"]
        indexes = [
            models.Index(fields=["-time_create"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"article_slug": self.slug})
