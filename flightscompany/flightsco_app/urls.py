from django.urls import path

from . import views

urlpatterns = [
    # главная страница
    path("", views.index, name="index"),
    # детальная страница предложения по слагу
    path("offers/<slug:article_slug>/", views.article_detail, name="article_detail"),
    # авторизация и профиль
    path("auth/", views.auth, name="auth"),
    path("profile/", views.profile, name="profile"),
    # информация о самолетах (int конвертер)
    path("planes/<int:plane_id>/", views.planes, name="planes"),
    # категории рейсов
    path("categories/", views.categories, name="categories"),
    path(
        "categories/<slug:category_slug>/",
        views.category_detail,
        name="category_detail",
    ),
    # детали рейса (int конвертер)
    path("flights/<int:flight_id>/", views.flight_detail, name="flight_detail"),
    # информация о маршруте (slug конвертер)
    path("routes/<slug:route_slug>/", views.route_info, name="route_info"),
    # поиск рейсов
    path("search/", views.search, name="search"),
    path("tags/<slug:tag_slug>/", views.tag_detail, name="tag_detail"),
    # бронирование
    path("booking/", views.booking, name="booking"),
    # архив по годам (int конвертер с проверкой)
    path("archive/<int:year>/", views.archive, name="archive"),
    # примеры перенаправлений
    path("old-booking/", views.old_booking_page, name="old_booking"),
    path("temp-redirect/", views.temp_redirect, name="temp_redirect"),
    path(
        "redirect-with-reverse/",
        views.redirect_with_reverse,
        name="redirect_with_reverse",
    ),
]
