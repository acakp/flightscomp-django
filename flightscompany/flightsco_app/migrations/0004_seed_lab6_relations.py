from django.db import migrations

CATEGORY_DATA = {
    "vnutrennie-reysy": "Внутренние рейсы",
    "mezhdunarodnye-reysy": "Международные рейсы",
}

TAG_DATA = {
    "vesna": "Весна",
    "leto": "Лето",
    "osen": "Осень",
    "gorodskoy-otdykh": "Городской отдых",
    "semeynyy-otdykh": "Семейный отдых",
    "gibkiy-tarif": "Гибкий тариф",
    "rannee-bronirovanie": "Раннее бронирование",
    "korotkiy-marshrut": "Короткий маршрут",
    "chernovik": "Черновик",
}

ARTICLE_TAG_MAP = {
    "vesennie-reysy-v-stambul": ["vesna", "gorodskoy-otdykh"],
    "letnie-predlozheniya-v-sochi": ["leto", "semeynyy-otdykh", "gibkiy-tarif"],
    "spetsialnyy-tarif-v-dubay": ["rannee-bronirovanie", "gibkiy-tarif"],
    "chernovik-osennego-napravleniya": ["osen", "chernovik"],
}

INTERNATIONAL_KEYWORDS = (
    "стамбул",
    "дубай",
    "минск",
    "ереван",
    "баку",
    "анталья",
    "тбилиси",
    "ташкент",
    "алматы",
)


def seed_lab6_relations(apps, schema_editor):
    FlightArticle = apps.get_model("flightsco_app", "FlightArticle")
    FlightCategory = apps.get_model("flightsco_app", "FlightCategory")
    FlightTag = apps.get_model("flightsco_app", "FlightTag")
    db_alias = schema_editor.connection.alias

    categories = {
        slug: FlightCategory.objects.using(db_alias).get_or_create(
            slug=slug,
            defaults={"name": name},
        )[0]
        for slug, name in CATEGORY_DATA.items()
    }
    tags = {
        slug: FlightTag.objects.using(db_alias).get_or_create(
            slug=slug,
            defaults={"name": name},
        )[0]
        for slug, name in TAG_DATA.items()
    }

    for article in FlightArticle.objects.using(db_alias).all():
        route = (article.route or "").lower()
        title = (article.title or "").lower()

        if any(keyword in route for keyword in INTERNATIONAL_KEYWORDS):
            article.category = categories["mezhdunarodnye-reysy"]
        else:
            article.category = categories["vnutrennie-reysy"]

        article.save(update_fields=["category"])

        tag_slugs = ARTICLE_TAG_MAP.get(article.slug, [])
        if not tag_slugs:
            if "весенн" in title:
                tag_slugs.append("vesna")
            if "летн" in title:
                tag_slugs.append("leto")
            if "осенн" in title:
                tag_slugs.append("osen")
            if "черновик" in title or article.status == 0:
                tag_slugs.append("chernovik")
            if article.category.slug == "mezhdunarodnye-reysy":
                tag_slugs.append("rannee-bronirovanie")
            else:
                tag_slugs.append("korotkiy-marshrut")

        article.tags.add(*[tags[slug] for slug in dict.fromkeys(tag_slugs)])


class Migration(migrations.Migration):
    dependencies = [
        ("flightsco_app", "0003_flightcategory_flighttag_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_lab6_relations, migrations.RunPython.noop),
    ]
