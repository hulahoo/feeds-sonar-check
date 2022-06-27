from django.db import models
from django.db.models import DateTimeField
from django.core.validators import MinValueValidator, MaxValueValidator


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
    name = models.CharField("Название тега", max_length=30)
    colour = models.CharField("Название тега", max_length=30, blank=True, null=True)
    exportable = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} | {self.colour}"

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class OrganizationContact(BaseModel):
    name = models.CharField("Название организации", max_length=64)
    uuid = models.CharField("Уникальный идентификатор", max_length=36, primary_key=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Контакт организации"
        verbose_name_plural = "Контакты организаций"


class Attribute(BaseModel):
    type = models.CharField("Тип", max_length=30)
    value = models.CharField("Значение", max_length=128)
    timestamp = models.CharField("Временная отметка", max_length=10)
    to_ids = models.BooleanField(blank=True, null=True)
    disable_correlation = models.BooleanField(blank=True, null=True)
    object_relation = models.CharField("Отношения объектов", max_length=15)
    category = models.CharField("Категория аттрибута", max_length=30)
    comment = models.CharField("Комментарий", max_length=128, blank=True, null=True)
    uuid = models.CharField("Уникальный идентификатор", max_length=36, primary_key=True)
    template_uuid = models.CharField(
        "Уникальный идентификатор темплейта", max_length=36, blank=True, null=True
    )
    object_relation = models.CharField("Отношение к объекту", max_length=30)
    value = models.CharField("Значение", max_length=128)

    def __str__(self):
        return f"{self.uuid}"

    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"


class MispObject(BaseModel):
    type = models.CharField("Тип аттрибута", max_length=30)
    timestamp = models.CharField("Временная отметка", max_length=10)
    template_version = models.CharField("Версия темплейта", max_length=10)
    sharing_group_id = models.CharField("ID группы распространения", max_length=10)
    description = models.CharField("Описание", max_length=128)
    deleted = models.BooleanField(blank=True, null=True)
    name = models.CharField("Название", max_length=32, unique=True)
    category = models.CharField("Категория аттрибута", max_length=30)
    comment = models.CharField("Комментарий", max_length=128, blank=True, null=True)
    uuid = models.CharField("Уникальный идентификатор", max_length=36, primary_key=True)
    object_relation = models.CharField("Отношение к объекту", max_length=30)
    value = models.CharField("Значение", max_length=128)
    attribute = models.ManyToManyField(
        Attribute,
        verbose_name="Аттрибут MISP Object'а",
        related_name="misp_object_attribute",
    )

    def __str__(self):
        return f"{self.uuid}"

    class Meta:
        verbose_name = "MISP объект"
        verbose_name_plural = "MISP объекты"


class MispEvent(BaseModel):
    threat_level_id = models.CharField("Id уровня угрозы", max_length=1)
    timestamp = models.CharField("Временная отметка последнего действия", max_length=10)
    info = models.CharField("Временная отметка", max_length=256)
    publish_timestamp = models.CharField("Временная отметка публикации", max_length=10)
    date = models.DateField("Дата возникновения")
    published = models.BooleanField("Опубликовано")
    analysis = models.CharField("Анализ", max_length=1)
    uuid = models.CharField("Уникальный идентификатор", max_length=36, primary_key=True)
    orgc = models.ForeignKey(OrganizationContact, on_delete=models.SET_NULL, null=True)
    tag = models.ManyToManyField(
        Tag, verbose_name="Теги", related_name="misp_event_tags"
    )
    attribute = models.ManyToManyField(
        Attribute,
        verbose_name="Аттрибут MISP Event'а",
        related_name="misp_event_attribute",
    )
    object = models.ManyToManyField(
        MispObject, verbose_name="Объект MISP Event'а", related_name="misp_event_object"
    )

    def __str__(self):
        return f"{self.info} | {self.uuid}"

    class Meta:
        verbose_name = "MISP событие"
        verbose_name_plural = "MISP события"


class Feed(BaseModel):
    MISP = "MISP"
    EMAIL_FROM = "FEMA"
    EMAIL_SUBJECT = "SEMA"
    MD5_HASH = "MD5H"
    SHA1_HASH = "SHA1"
    SHA256_HASH = "SHA2"
    IP = "IPAD"
    URL = "URLS"
    DOMAIN = "DOMN"
    FILENAME = "FILE"
    REGISTRY = "REGS"

    CSV_FILE = "CSV"
    JSON_FILE = "JSN"
    XML_FILE = "XML"
    TXT_FILE = "TXT"

    NO_AUTH = "NAU"
    API = "API"
    BASIC = "BSC"
    NEVER = "NVR"
    THIRTY_MINUTES = "M30"
    ONE_HOUR = "HR1"
    TWO_HOURS = "HR2"
    FOUR_HOURS = "HR4"
    EIGHT_HOURS = "HR8"
    SIXTEEN_HOURS = "H16"
    TWENTY_FOUR_HOURS = "H24"

    TYPE_OF_FEED_CHOICES = [
        (EMAIL_FROM, "Email's origin"),
        (EMAIL_SUBJECT, "Email's subject"),
        (MD5_HASH, "File hashe MD5"),
        (SHA1_HASH, "File hashe SHA1"),
        (SHA256_HASH, "File hashe SHA256"),
        (FILENAME, "File name"),
        (REGISTRY, "Registry"),
        (IP, "IP adresses"),
        (URL, "Full URL's"),
        (DOMAIN, "Domain's"),
    ]
    FORMAT_OF_FEED_CHOICES = [
        (CSV_FILE, "CSV формат"),
        (JSON_FILE, "JSON формат"),
        (XML_FILE, "XML формат"),
        (TXT_FILE, "TXT формат"),
    ]
    TYPE_OF_AUTH_CHOICES = [
        (NO_AUTH, "Отсуствует"),
        (API, "API token"),
        (BASIC, "HTTP basic"),
    ]
    POLLING_FREQUENCY_CHOICES = [
        (NEVER, "Никогда"),
        (THIRTY_MINUTES, "30 минут"),
        (ONE_HOUR, "1 час"),
        (TWO_HOURS, "2 часа"),
        (FOUR_HOURS, "4 часа"),
        (EIGHT_HOURS, "8 часов"),
        (SIXTEEN_HOURS, "16 часов"),
        (TWENTY_FOUR_HOURS, "24 часа"),
    ]

    type_of_feed = models.CharField(
        "Тип фида", max_length=4, choices=TYPE_OF_FEED_CHOICES, default=IP
    )
    format_of_feed = models.CharField(
        "Формат фида", max_length=3, choices=FORMAT_OF_FEED_CHOICES, default=TXT_FILE
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
    field_names = models.CharField(
        "Названия полей через запятую", max_length=128, blank=True, null=True
    )
    sertificate = models.FileField("Файл сертификат", blank=True, null=True)
    vendor = models.CharField("Вендор", max_length=32)
    name = models.CharField("Название фида", max_length=32, unique=True)
    link = models.CharField("Ссылка на фид", max_length=100)
    confidence = models.IntegerField(
        "Достоверность", validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    records_quantity = models.IntegerField("Количество записей", blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Фид"
        verbose_name_plural = "Фиды"


class Indicator(BaseModel):
    EMAIL_FROM = "FEMA"
    EMAIL_SUBJECT = "SEMA"
    MD5_HASH = "MD5H"
    SHA1_HASH = "SHA1"
    SHA256_HASH = "SHA2"
    IP = "IPAD"
    URL = "URLS"
    DOMAIN = "DOMN"
    FILENAME = "FILE"
    REGISTRY = "REGS"

    TYPE_OF_INDICATOR_CHOICES = [
        (EMAIL_FROM, "Email's origin"),
        (EMAIL_SUBJECT, "Email's subject"),
        (MD5_HASH, "File hashe MD5"),
        (SHA1_HASH, "File hashe SHA1"),
        (SHA256_HASH, "File hashe SHA256"),
        (FILENAME, "File name"),
        (REGISTRY, "Registry"),
        (IP, "IP adresses"),
        (URL, "Full URL's"),
        (DOMAIN, "Domain's"),
    ]

    type = models.CharField(
        "Тип индикатора", max_length=4, choices=TYPE_OF_INDICATOR_CHOICES, default=IP
    )
    uuid = models.CharField(
        "Уникальный идентификатор индикатора", unique=True, max_length=36
    )
    category = models.CharField(
        "Категория индикатора", max_length=128, blank=True, null=True
    )
    value = models.CharField("Значение индикатора", max_length=256)
    updated_date = DateTimeField("Дата последнего обновления")
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

    def __str__(self):
        return f"{self.value}"

    class Meta:
        verbose_name = "Индикатор"
        verbose_name_plural = "Индикаторы"
