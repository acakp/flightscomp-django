from django.db import migrations


def seed_articles(apps, schema_editor):
    FlightArticle = apps.get_model("flightsco_app", "FlightArticle")
    FlightArticle.objects.bulk_create(
        [
            FlightArticle(
                title="Весенние рейсы в Стамбул",
                slug="vesennie-reysy-v-stambul",
                content=(
                    "Подборка подходит для короткого отпуска и деловых поездок.\n\n"
                    "В стоимость включена ручная кладь, а время вылета подобрано так, "
                    "чтобы пассажиры могли удобно спланировать трансфер и заселение."
                ),
                route="Казань — Стамбул",
                price="18490.00",
                status=1,
            ),
            FlightArticle(
                title="Летние предложения в Сочи",
                slug="letnie-predlozheniya-v-sochi",
                content=(
                    "Маршрут ориентирован на семейный отдых и поездки выходного дня.\n\n"
                    "Доступны утренние и вечерние вылеты, а также гибкие условия возврата "
                    "в рамках выбранного тарифа."
                ),
                route="Москва — Сочи",
                price="12600.00",
                status=1,
            ),
            FlightArticle(
                title="Специальный тариф в Дубай",
                slug="spetsialnyy-tarif-v-dubay",
                content=(
                    "Предложение рассчитано на пассажиров, которые планируют поездку заранее.\n\n"
                    "Маршрут особенно удобен для туристов: минимальное время пересадки и "
                    "возможность добавить багаж по сниженной цене."
                ),
                route="Санкт-Петербург — Дубай",
                price="27350.00",
                status=1,
            ),
            FlightArticle(
                title="Черновик осеннего направления",
                slug="chernovik-osennego-napravleniya",
                content="Служебная запись для демонстрации работы пользовательского менеджера.",
                route="Казань — Минск",
                price="9800.00",
                status=0,
            ),
        ]
    )


def unseed_articles(apps, schema_editor):
    FlightArticle = apps.get_model("flightsco_app", "FlightArticle")
    FlightArticle.objects.filter(
        slug__in=[
            "vesennie-reysy-v-stambul",
            "letnie-predlozheniya-v-sochi",
            "spetsialnyy-tarif-v-dubay",
            "chernovik-osennego-napravleniya",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("flightsco_app", "0001_initial")]

    operations = [migrations.RunPython(seed_articles, unseed_articles)]
