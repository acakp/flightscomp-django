from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import FlightArticle, FlightCategory, FlightTag, UploadedFile


class TagPresenceFilter(admin.SimpleListFilter):
    title = "Наличие тегов"
    parameter_name = "tag_state"

    def lookups(self, request, model_admin):
        return [
            ("with_tags", "С тегами"),
            ("without_tags", "Без тегов"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "with_tags":
            return queryset.filter(tags__isnull=False).distinct()
        if self.value() == "without_tags":
            return queryset.filter(tags__isnull=True)
        return queryset


@admin.register(FlightArticle)
class FlightArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "post_photo",
        "route",
        "price",
        "time_create",
        "status",
        "category",
        "brief_info",
    )
    list_display_links = ("title",)
    list_editable = ("status", "category")
    ordering = ("-time_create", "title")
    list_per_page = 5
    list_select_related = ("category",)
    actions = ("set_published", "set_draft")
    search_fields = ("title__startswith", "category__name", "route")
    list_filter = (TagPresenceFilter, "category", "status")
    fields = (
        "title",
        "slug",
        "content",
        "route",
        "price",
        "photo",
        "post_photo",
        "category",
        "tags",
        "status",
        "time_create",
        "time_update",
    )
    readonly_fields = ("post_photo", "time_create", "time_update")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    save_on_top = True

    @admin.display(description="Краткая информация")
    def brief_info(self, article: FlightArticle):
        content_length = len(article.content.strip()) if article.content else 0
        return f"{article.route}, {content_length} символов"

    @admin.display(description="Изображение")
    def post_photo(self, article: FlightArticle):
        if article.photo:
            return mark_safe(f"<img src='{article.photo.url}' width='50'>")
        return "Без фото"

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(status=FlightArticle.Status.PUBLISHED)
        self.message_user(request, f"Изменено {count} записи(ей).")

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(status=FlightArticle.Status.DRAFT)
        self.message_user(
            request,
            f"{count} записи(ей) сняты с публикации!",
            messages.WARNING,
        )


@admin.register(FlightCategory)
class FlightCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    ordering = ("name",)
    search_fields = ("name__startswith",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(FlightTag)
class FlightTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    ordering = ("name",)
    search_fields = ("name__startswith",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "time_create")
    list_display_links = ("id", "file")
    ordering = ("-time_create",)
