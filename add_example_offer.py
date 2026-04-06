from flightsco_app.models import FlightArticle, FlightCategory, FlightTag

category = FlightCategory.objects.get(slug="mezhdunarodnye-reysy")
summer_tag = FlightTag.objects.get(slug="leto")
family_tag = FlightTag.objects.get(slug="semeynyy-otdykh")

offer, created = FlightArticle.objects.update_or_create(
    slug="example-offer-antalya",
    defaults={
        "title": "TESTTESTTESTTEST",
        "content": "privet",
        "route": "Магадан - Москва",
        "price": "24990.00",
        "category": category,
        "status": FlightArticle.Status.PUBLISHED,
    },
)
