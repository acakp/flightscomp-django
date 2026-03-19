from django.shortcuts import render, redirect
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponsePermanentRedirect,
    Http404,
)
from django.urls import reverse


# Create your views here.
def index(request):
    return render(request, "flightsco_app/index.html")


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
    return HttpResponse(f"<h1>Самолет #{plane_id}</h1><p>Информация о самолете</p>")


def categories(request):
    if request.GET:
        category_type = request.GET.get("type", "all")
        print(f"Категория: {category_type}")
    return HttpResponse("<h1>Категории рейсов</h1><p>Список категорий</p>")


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
    return HttpResponseNotFound(
        "<h1>Страница не найдена</h1>"
        "<p>Запрошенная страница не существует или была удалена.</p>"
        "<p><a href='/'>Вернуться на главную</a></p>"
    )


def server_error(request):
    return HttpResponse(
        "<h1>Ошибка сервера (500)</h1>"
        "<p>Произошла ошибка при обработке запроса.</p>"
        "<p><a href='/'>Вернуться на главную</a></p>",
        status=500,
    )
