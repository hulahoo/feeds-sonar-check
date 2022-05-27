from tabnanny import verbose
from django.db import models
from django.db.models import DateTimeField


class CreationDateTimeField(DateTimeField):
    """
    CreationDateTimeField
    By default, sets editable=False, blank=True, auto_now_add=True
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("editable", False)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("auto_now_add", True)
        DateTimeField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.editable is not False:
            kwargs["editable"] = True
        if self.blank is not True:
            kwargs["blank"] = False
        if self.auto_now_add is not False:
            kwargs["auto_now_add"] = True
        return name, path, args, kwargs


class IndicatorModel(models.Model):
    """
    IndicatorModel
    An abstract base class model that provides self-managed
    "created" field and "origin" field.
    """

    created = CreationDateTimeField("создано")
    origin = models.CharField("источник", max_length=128)

    class Meta:
        get_latest_by = "modified"
        abstract = True


class Domains(IndicatorModel):
    domain_name = models.CharField("Доменное имя", max_length=256, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.domain_name}"

    class Meta:
        verbose_name = "Домен"
        verbose_name_plural = "Домены"


class IPAddress(IndicatorModel):
    address = models.CharField("IP адрес", max_length=39, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.address}"

    class Meta:
        verbose_name = "IP адрес"
        verbose_name_plural = "IP адреса"


class FullURL(IndicatorModel):
    url = models.CharField("URL", max_length=256, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.url}"

    class Meta:
        verbose_name = "URL"
        verbose_name_plural = "URL'ы"


class Email(IndicatorModel):
    email = models.CharField("Почта", max_length=128, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.email}"

    class Meta:
        verbose_name = "Адрес электронной почты"
        verbose_name_plural = "Адреса электронных почт"


class FileHash(IndicatorModel):
    hash = models.CharField("Хэш файла", max_length=128, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.hash}"

    class Meta:
        verbose_name = "Хэш файла"
        verbose_name_plural = "Хэши файлов"
