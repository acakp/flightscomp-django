from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FlightArticle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                (
                    "slug",
                    models.SlugField(db_index=True, max_length=255, unique=True, verbose_name="URL"),
                ),
                ("content", models.TextField(blank=True, verbose_name="Описание")),
                ("route", models.CharField(max_length=255, verbose_name="Маршрут")),
                (
                    "price",
                    models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Стоимость"),
                ),
                (
                    "time_create",
                    models.DateTimeField(auto_now_add=True, verbose_name="Время создания"),
                ),
                (
                    "time_update",
                    models.DateTimeField(auto_now=True, verbose_name="Время изменения"),
                ),
                (
                    "status",
                    models.IntegerField(
                        choices=[(0, "Черновик"), (1, "Опубликовано")],
                        default=0,
                        verbose_name="Статус публикации",
                    ),
                ),
            ],
            options={
                "verbose_name": "Предложение по перелету",
                "verbose_name_plural": "Предложения по перелетам",
                "ordering": ["-time_create"],
                "indexes": [
                    models.Index(fields=["-time_create"], name="flightsco_a_time_cr_6c217f_idx"),
                    models.Index(fields=["status"], name="flightsco_a_status_77f33b_idx"),
                ],
            },
        ),
    ]
