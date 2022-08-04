import audioop

from django.db import models
from django.db.models import DateTimeField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from intelhandler.constants import *


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


class ModificationDateTimeField(CreationDateTimeField):
    """
    ModificationDateTimeField
    By default, sets editable=False, blank=True, auto_now=True
    Sets value to now every time the object is saved.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("auto_now", True)
        DateTimeField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.auto_now is not False:
            kwargs["auto_now"] = True
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        if not getattr(model_instance, "update_modified", True):
            return getattr(model_instance, self.attname)
        return super().pre_save(model_instance, add)


class BaseModel(models.Model):
    """
    BaseModel
    An abstract base class model that provides self-managed
    "created" field and "modified" field.
    """

    created = CreationDateTimeField("создано")
    modified = ModificationDateTimeField("изменено")

    # origin = models.CharField("источник", max_length=128)

    class Meta:
        get_latest_by = "modified"
        abstract = True


class Tag(BaseModel):
    """
    Модель тега.
    """

    name = models.CharField("Название тега", max_length=30)
    colour = models.CharField("Название тега", max_length=30, blank=True, null=True)
    exportable = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} | {self.colour}"

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Indicator(BaseModel):
    """
    Модель индикатора.
    """

    type = models.CharField(
        "Тип индикатора", max_length=4, choices=TYPE_OF_INDICATOR_CHOICES, default=IP
    )
    uuid = models.CharField(
        "Уникальный идентификатор индикатора", unique=True, max_length=255
    )
    category = models.CharField(
        "Категория индикатора", max_length=128, blank=True, null=True
    )
    value = models.CharField("Значение индикатора", max_length=256)
    weight = models.IntegerField(
        "Вес", validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    tag = models.ManyToManyField(Tag, "Теги")
    false_detected = models.IntegerField(
        "счетчик ложных срабатываний", validators=[MinValueValidator(0)], default=0
    )
    positive_detected = models.IntegerField(
        "счетчик позитивных срабатываний", validators=[MinValueValidator(0)], default=0
    )
    detected = models.IntegerField(
        "общий счетчик срабатываний", validators=[MinValueValidator(0)], default=0
    )
    first_detected_date = DateTimeField(
        "Дата первого срабатывания", blank=True, null=True
    )
    last_detected_date = DateTimeField(
        "Дата последнего срабатывания", blank=True, null=True
    )
    # Данные об источнике
    supplier_name = models.CharField("Название источника", max_length=128)
    supplier_vendor_name = models.CharField("Название поставщика ", max_length=128)
    supplier_type = models.CharField("Тип поставщика", max_length=64)
    supplier_confidence = models.IntegerField(
        "Достоверность", validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    supplier_created_date = DateTimeField(
        "Дата последнего обновления", blank=True, null=True
    )
    # Контекст
    ioc_context_exploits_md5 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_exploits_sha1 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_exploits_sha256 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_exploits_threat = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_av_verdict = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_ip = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_md5 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_sha1 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_sha256 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_affected_products_product = models.CharField(
        max_length=64, blank=True, null=True
    )
    joc_context_domains = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_file_names = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_file_size = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_file_type = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_files_behaviour = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_files_md5 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_files_sha1 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_files_sha256 = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_files_threat = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_malware = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_mask = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_popularity = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_port = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_protocol = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_publication_name = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_severity = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_type = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_url = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_urls_url = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_vendors_vendor = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_geo = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_id = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_industry = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_ip = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_ip_geo = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_ip_whois_asn = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_ip_whois_contact_abuse_country = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_contact_abuse_email = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_contact_abuse_name = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_contact_owner_city = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_contact_owner_code = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_contact_owner_country = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_contact_owner_email = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_contact_owner_name = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_country = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_created = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_desrc = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_ip_whois_net_name = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_net_range = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_ip_whois_updated = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_whois_mx = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_mx_ips = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_ns = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_ns_ips = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_city = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_country = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_created = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_domain = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_email = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_expires = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_name = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_org = models.CharField(max_length=64, blank=True, null=True)
    ioc_context_whois_registrar_email = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_whois_registrar_name = models.CharField(
        max_length=64, blank=True, null=True
    )
    ioc_context_whois_updated = models.CharField(max_length=64, blank=True, null=True)

    # время жизни
    ttl = models.DateTimeField("Дата удаления", blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.value}"

    @classmethod
    def get_model_fields(cls):
        return {i.attname: list(i.class_lookups.keys()) for i in cls._meta.fields}

    class Meta:
        verbose_name = "Индикатор"
        verbose_name_plural = "Индикаторы"


class ParsingRule(BaseModel):
    """
    Модель правила для парсинга (CSV)
    """

    class Meta:
        verbose_name = "Правило парсинга"
        verbose_name_plural = "Правила парсинга"


class Feed(BaseModel):
    """
    Модель фида - источника данных.
    """

    type_of_feed = models.CharField(
        "Тип фида", max_length=4, choices=TYPE_OF_FEED_CHOICES, default=IP
    )
    format_of_feed = models.CharField(
        "Формат фида", max_length=15, choices=FORMAT_OF_FEED_CHOICES, default=TXT_FILE
    )
    auth_type = models.CharField(
        "Тип авторизации", max_length=3, choices=TYPE_OF_AUTH_CHOICES, default=NO_AUTH
    )
    polling_frequency = models.CharField(
        "Частота обновления фида",
        max_length=3,
        choices=POLLING_FREQUENCY_CHOICES,
        default=NEVER,
    )

    auth_login = models.CharField(
        "Логин для авторизации", max_length=32, blank=True, null=True
    )
    auth_password = models.CharField(
        "Пароль для авторизации", max_length=64, blank=True, null=True
    )
    ayth_querystring = models.CharField(
        "Строка для авторизации", max_length=128, blank=True, null=True
    )
    separator = models.CharField(
        "Разделитель для CSV формата", max_length=8, blank=True, null=True
    )
    parsing_rules = models.ManyToManyField(
        ParsingRule,
        verbose_name="Правила для парсинга",
        related_name="feed_parsing_rules",
        blank=True,
    )
    custom_field = models.CharField(
        "Кастомное поле", max_length=128, blank=True, null=True
    )
    sertificate = models.FileField("Файл сертификат", blank=True, null=True)
    vendor = models.CharField("Вендор", max_length=32)
    name = models.CharField("Название фида", max_length=32, unique=True)
    link = models.CharField("Ссылка на фид", max_length=255)
    confidence = models.IntegerField(
        "Достоверность", validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    records_quantity = models.IntegerField("Количество записей", blank=True, null=True)
    indicators = models.ManyToManyField(
        Indicator, related_name="feeds", verbose_name="Индикатор", blank=True
    )

    update_status = models.CharField(max_length=15, choices=TYPE_OF_STATUS_UPDATE, default=ENABLED)

    ts = models.DateTimeField(auto_now_add=True)

    source = models.ForeignKey("Source", on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_model_fields(cls):
        return [i.attname for i in cls._meta.fields]

    class Meta:
        verbose_name = "Фид"
        verbose_name_plural = "Фиды"


class Source(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    is_instead_full = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    provider_name = models.CharField(max_length=255)
    path = models.TextField()
    certificate = models.FileField("Путь к сертификату", blank=True, null=True)
    authenticity = models.IntegerField(
        "Достоверность", validators=[MaxValueValidator(100), MinValueValidator(0)],
        default=0
    )
    format = models.CharField(
        "Формат", max_length=15, choices=TYPE_OF_FORMAT, default=CSV
    )

    auth_type = models.CharField(
        "Тип авторизации", max_length=3, choices=TYPE_OF_AUTH_CHOICES, default=NO_AUTH
    )
    auth_login = models.CharField(
        "Логин для авторизации", max_length=32, blank=True, null=True
    )
    auth_password = models.CharField(
        "Пароль для авторизации", max_length=64, blank=True, null=True
    )

    max_rows = models.IntegerField(default=None, null=True)
    raw_indicators = models.TextField(default=None, null=True)
    update_time_period = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'
