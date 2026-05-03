from django.conf import settings

def get_flights_context(request):
    menu = [
        {"title": "Рейсы", "url_name": "search"},
    ]
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            menu.append({"title": "Добавить", "url_name": "add_offer"})
        if request.user.is_superuser:
            menu.append({"title": "Пользователи", "url_name": "users:manage_users"})
            
    menu.append({"title": "Загрузка", "url_name": "about"})
    
    return {
        "mainmenu": menu,
        "YANDEX_MAPS_API_KEY": getattr(settings, 'YANDEX_MAPS_API_KEY', ''),
    }
