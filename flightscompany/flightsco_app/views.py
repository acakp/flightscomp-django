from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import FlightArticle, FlightCategory, FlightTag


def _get_offer_queryset():
    return FlightArticle.published.select_related("category").prefetch_related("tags")


def _build_catalog_context(
    *,
    articles,
    page_heading,
    page_description,
    page_title=None,
    selected_category=None,
    selected_tag=None,
):
    return {
        "articles": articles,
        "categories": FlightCategory.objects.all(),
        "all_tags": FlightTag.objects.all(),
        "page_heading": page_heading,
        "page_description": page_description,
        "page_title": page_title or f"{page_heading} - Флайтс Компани",
        "selected_category": selected_category,
        "selected_tag": selected_tag,
    }


# Create your views here.
def index(request):
    articles = _get_offer_queryset()
    context = _build_catalog_context(
        articles=articles,
        page_heading="Актуальные предложения",
        page_description="Подборка предложений из базы данных с фильтрацией по категориям и тегам.",
        page_title="Дешёвые авиабилеты - Флайтс Компани",
    )
    return render(request, "flightsco_app/index.html", context)


def article_detail(request, article_slug):
    article = get_object_or_404(
        _get_offer_queryset(),
        slug=article_slug,
    )
    context = {
        "article": article,
    }
    return render(request, "flightsco_app/article_detail.html", context)


def auth(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        # в реальной здесь была бы проверка учетных данных
        # пока просто перенаправляем на профиль
        return redirect("profile")
    return render(request, "flightsco_app/auth.html")


def profile(request):
    return render(request, "flightsco_app/profile.html")


def planes(request, plane_id):
    return HttpResponse("<h1>Самолет #{plane_id}</h1><p>Информация о самолете</p>")


def categories(request):
    context = _build_catalog_context(
        articles=_get_offer_queryset(),
        page_heading="Каталог по категориям",
        page_description="Все опубликованные предложения с возможностью перейти в нужную рубрику.",
        page_title="Категории перелетов - Флайтс Компани",
    )
    return render(request, "flightsco_app/index.html", context)


def category_detail(request, category_slug):
    category = get_object_or_404(FlightCategory, slug=category_slug)
    articles = _get_offer_queryset().filter(category=category)
    context = _build_catalog_context(
        articles=articles,
        page_heading=f"Категория: {category.name}",
        page_description="Предложения, связанные с выбранной рубрикой.",
        selected_category=category,
    )
    return render(request, "flightsco_app/index.html", context)


def flight_detail(request, flight_id):
    return HttpResponse(f"<h1>Рейс #{flight_id}</h1><p>Детали рейса</p>")


def route_info(request, route_slug):
    return HttpResponse(
        f"<h1>Маршрут: {route_slug}</h1><p>Информация о направлении</p>"
    )


def search(request):
    if request.method == "GET" and request.GET:
        origin = request.GET.get("origin", "")
        destination = request.GET.get("destination", "")
        departure_date = request.GET.get("departure", "")

        print(f"Поиск рейсов: {origin} -> {destination}, дата: {departure_date}")

        if origin and destination:
            return HttpResponse(
                f"<h1>Результаты поиска</h1>"
                f"<p>Откуда: {origin}</p>"
                f"<p>Куда: {destination}</p>"
                f"<p>Дата: {departure_date or 'Не указана'}</p>"
            )

    return render(request, "flightsco_app/search.html")


def tag_detail(request, tag_slug):
    tag = get_object_or_404(FlightTag, slug=tag_slug)
    articles = _get_offer_queryset().filter(tags=tag).distinct()
    context = _build_catalog_context(
        articles=articles,
        page_heading=f"Тег: {tag.name}",
        page_description="Предложения, отмеченные выбранным тегом.",
        selected_tag=tag,
    )
    return render(request, "flightsco_app/index.html", context)


def booking(request):
    if request.method == "POST":
        # Обработка данных формы бронирования
        passenger_name = request.POST.get("passenger_name")
        flight_id = request.POST.get("flight_id")
        email = request.POST.get("email")

        # В реальной реализации здесь было бы сохранение бронирования
        print(f"Бронирование: {passenger_name}, рейс {flight_id}, email: {email}")

        # Перенаправление на страницу профиля после успешного бронирования
        return redirect("profile")

    return HttpResponse("<h1>Форма бронирования</h1>")


def archive(request, year):
    if year > 2025:
        # Генерация исключения 404 для будущих лет
        raise Http404("Архив за этот год еще не доступен")
    return HttpResponse(f"<h1>Архив рейсов за {year} год</h1>")


def old_booking_page(request):
    return redirect("index", permanent=True)


def temp_redirect(request):
    return redirect("categories")


def redirect_with_reverse(request):
    # Вычисление URL с помощью reverse()
    url = reverse("flight_detail", args=[123])
    return HttpResponsePermanentRedirect(url)


def page_not_found(request, exception):
    return render(request, "flightsco_app/404.html", status=404)


def server_error(request):
    return render(request, "flightsco_app/500.html", status=500)
