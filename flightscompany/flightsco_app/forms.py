from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.utils.deconstruct import deconstructible

from .models import FlightArticle, FlightCategory, FlightTag


@deconstructible
class RussianTitleValidator:
    allowed_chars = (
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"
        "абвгдеёжзийклмнопрстуфхцчшщьыъэюя"
        "0123456789- "
    )
    code = "russian"

    def __init__(self, message=None):
        self.message = (
            message
            if message
            else "Должны быть только русские символы, цифры, дефис и пробел."
        )

    def __call__(self, value):
        if not (set(value) <= set(self.allowed_chars)):
            raise ValidationError(self.message, code=self.code, params={"value": value})


class FlightSearchForm(forms.Form):
    PASSENGER_CHOICES = [
        ("1", "1 пассажир"),
        ("2", "2 пассажира"),
        ("3", "3 пассажира"),
        ("4", "4 пассажира"),
        ("5+", "5+ пассажиров"),
    ]

    origin = forms.CharField(
        max_length=100,
        label="Откуда",
        widget=forms.TextInput(
            attrs={"class": "form-control p-3", "placeholder": "Город вылета"}
        ),
    )
    destination = forms.CharField(
        max_length=100,
        label="Куда",
        widget=forms.TextInput(
            attrs={"class": "form-control p-3", "placeholder": "Город прилета"}
        ),
    )
    departure = forms.DateField(
        required=False,
        label="Дата вылета",
        widget=forms.DateInput(
            attrs={"class": "form-control p-3", "type": "date"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
    )
    return_date = forms.DateField(
        required=False,
        label="Дата возвращения",
        widget=forms.DateInput(
            attrs={"class": "form-control p-3", "type": "date"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
    )
    passengers = forms.ChoiceField(
        choices=PASSENGER_CHOICES,
        label="Пассажиры",
        initial="1",
        widget=forms.Select(attrs={"class": "form-select p-3"}),
    )


class AddFlightArticleForm(forms.ModelForm):
    title = forms.CharField(
        max_length=255,
        min_length=5,
        label="Заголовок",
        validators=[RussianTitleValidator()],
        error_messages={
            "min_length": "Слишком короткий заголовок",
            "required": "Без заголовка форма не может быть отправлена",
        },
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    slug = forms.SlugField(
        max_length=255,
        label="URL",
        validators=[
            MinLengthValidator(5, message="Минимум 5 символов"),
            MaxLengthValidator(100, message="Максимум 100 символов"),
        ],
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    category = forms.ModelChoiceField(
        queryset=FlightCategory.objects.all(),
        empty_label="Категория не выбрана",
        label="Категория",
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=FlightTag.objects.all(),
        required=False,
        label="Теги",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = FlightArticle
        fields = [
            "title",
            "slug",
            "content",
            "route",
            "price",
            "photo",
            "status",
            "category",
            "tags",
        ]
        labels = {
            "content": "Описание",
            "route": "Маршрут",
            "price": "Стоимость",
            "photo": "Изображение",
            "status": "Статус публикации",
        }
        widgets = {
            "content": forms.Textarea(attrs={"cols": 50, "rows": 5}),
            "route": forms.TextInput(attrs={"class": "form-input"}),
            "price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) > 50:
            raise ValidationError("Длина превышает 50 символов")
        return title


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Файл")
