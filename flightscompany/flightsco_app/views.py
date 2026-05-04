import json
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import AddFlightArticleForm, FlightSearchForm, UploadFileForm
from .models import FlightArticle, FlightCategory, FlightTag, UploadedFile


def _get_offer_queryset():
    return FlightArticle.published.select_related("category").prefetch_related("tags")


@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            api_key = settings.YANDEX_GPT_API_KEY
            folder_id = settings.YANDEX_FOLDER_ID

            if not api_key or not folder_id:
                return JsonResponse({"reply": "Пожалуйста, настройте YANDEX_GPT_API_KEY и YANDEX_FOLDER_ID в .env файле."})

            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Api-Key {api_key}",
                "x-folder-id": folder_id,
                "Content-Type": "application/json"
            }

            payload = {
                "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": "1000"
                },
                "messages": [
                    {
                        "role": "system",
                        "text": "Ты - полезный и вежливый чат-бот для сайта бронирования авиабилетов 'Флайтс Компани'. Отвечай на вопросы о рейсах, бронировании и путешествиях кратко и по делу."
                    },
                    {
                        "role": "user",
                        "text": user_message
                    }
                ]
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result_data = response.json()
            reply_text = result_data["result"]["alternatives"][0]["message"]["text"]

            return JsonResponse({"reply": reply_text})

        except Exception as e:
            return JsonResponse({"reply": f"Произошла ошибка при обращении к API: {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


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


@login_required
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
    search_result = None

    if request.GET:
        form = FlightSearchForm(request.GET)
        if form.is_valid():
            search_result = form.cleaned_data
    else:
        form = FlightSearchForm()

    context = {
        "form": form,
        "search_result": search_result,
    }
    return render(request, "flightsco_app/search.html", context)


def is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_staff_user)
def add_offer(request):
    if request.method == "POST":
        form = AddFlightArticleForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.author = request.user
            offer.save()
            form.save_m2m()
            return redirect("index")
    else:
        form = AddFlightArticleForm(
            initial={"status": FlightArticle.Status.PUBLISHED}
        )

    context = {
        "title": "Добавление предложения",
        "form": form,
    }
    return render(request, "flightsco_app/add_offer.html", context)


def about(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            UploadedFile.objects.create(file=form.cleaned_data["file"])
            return redirect("about")
    else:
        form = UploadFileForm()

    context = {
        "title": "О сервисе",
        "form": form,
        "uploads": UploadedFile.objects.all()[:5],
    }
    return render(request, "flightsco_app/about.html", context)


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


def office_map(request):
    return render(request, "flightsco_app/map_office.html", {"title": "Офис на карте"})


def redirect_with_reverse(request):
    # Вычисление URL с помощью reverse()
    url = reverse("flight_detail", args=[123])
    return HttpResponsePermanentRedirect(url)


def page_not_found(request, exception):
    return render(request, "flightsco_app/404.html", status=404)


def server_error(request):
    return render(request, "flightsco_app/500.html", status=500)
