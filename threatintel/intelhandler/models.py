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


class BaseModel(models.Model):
    """
    BaseModel
    An abstract base class model that provides self-managed
    "created" field and "origin" field.
    """

    created = CreationDateTimeField("создано")
    origin = models.CharField("источник", max_length=128)

    class Meta:
        get_latest_by = "modified"
        abstract = True


class Domains(BaseModel):
    domain_name = models.CharField("Доменное имя", max_length=256, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.domain_name}"

    class Meta:
        verbose_name = "Домен"
        verbose_name_plural = "Домены"


class IPAddress(BaseModel):
    address = models.CharField("IP адрес", max_length=39, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.address}"

    class Meta:
        verbose_name = "IP адрес"
        verbose_name_plural = "IP адреса"


class FullURL(BaseModel):
    url = models.CharField("URL", max_length=256, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.url}"

    class Meta:
        verbose_name = "URL"
        verbose_name_plural = "URL'ы"


class Email(BaseModel):
    email = models.CharField("Почта", max_length=128, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.email}"

    class Meta:
        verbose_name = "Адрес электронной почты"
        verbose_name_plural = "Адреса электронных почт"


class FileHash(BaseModel):
    hash = models.CharField("Хэш файла", max_length=128, unique=True)

    def __str__(self):
        return f"{self.created.date()} | {self.hash}"

    class Meta:
        verbose_name = "Хэш файла"
        verbose_name_plural = "Хэши файлов"


class OrganizationContact(CreationDateTimeField):
    name = models.CharField("Название организации", max_length="30")
    uuid = models.CharField("Уникальный идентификатор", max_length=36, primary_key=True)

    def __str__(self):
        return f"{self.name} | {self.uuid}"

    class Meta:
        verbose_name = "Контакт организации"
        verbose_name_plural = "Контакты организаций"


class Tag(CreationDateTimeField):
    name = models.CharField("Название тега", max_length="30")
    colour = models.CharField("Название тега", max_length="30", blank=True, null=True)
    exportable = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Attribute(CreationDateTimeField):
    type = models.CharField("Тип аттрибута", max_length="30")
    timestamp = models.CharField("Временная отметка", max_length=10)
    to_ids = models.BooleanField(blank=True, null=True)
    category = models.CharField("Категория аттрибута", max_length="30")
    comment = models.CharField("Комментарий", max_length=128, blank=True, null=True)
    uuid = models.CharField("Уникальный идентификатор", max_length=36, primary_key=True)
    object_relation = models.CharField("Отношение к объекту", max_length="30")
    value = models.CharField("Значение", max_length="128")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class MispEvent(BaseModel):
    threat_level_id = models.CharField("Id уровня угрозы", max_length=1)
    timestamp = models.CharField("Временная отметка последнего действия", max_length=10)
    info = models.CharField("Временная отметка", max_length=256)
    publish_timestamp = models.CharField("Временная отметка публикации", max_length=10)
    date = models.DateField("Дата возникновения")
    published = models.BooleanField("Опубликовано")
    analysis = models.CharField("Анализ", max_length=1)
    uuid = models.CharField("Уникальный идентификатор", max_length=36, primary_key=True)
    orgc = models.ForeignKey(OrganizationContact, on_delete="SET_NULL", null=True)
    tag = models.ForeignKey(Tag, on_delete="SET_NULL", null=True)

    def __str__(self):
        return f"{self.created.date()} | {self.uuid}"

    class Meta:
        verbose_name = "Misp событие"
        verbose_name_plural = "Misp события"


class Feed(CreationDateTimeField):

    # type_of_feed = pass
    link = models.CharField("Ссылка на фид", max_length=100)