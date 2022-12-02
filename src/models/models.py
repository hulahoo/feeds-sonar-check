from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column, Integer, String, ForeignKey, func,
    DateTime, Text, Boolean, Enum, CheckConstraint, LargeBinary
)

from src.commons.enums import (
    StatusUpdateEnum, FormatTypeEnum, TypesEnum,
    FeedFormatEnum, AuthEnum, PollingFrequencyEnum
)
from src.models.abstract import IDBase, TimestampBase


class IndicatorTagM2MTable(IDBase):
    __tablename__ = "indicator_tag_m2m_table"
    indicator_id = Column(
        Integer,
        ForeignKey("indicator.id"),
        primary_key=True
    )
    tag_id = Column(
        Integer,
        ForeignKey("tag.id"),
        primary_key=True
    )


class Tag(IDBase, TimestampBase):
    """
    Модель тега.
    """
    __tablename__ = "tag"

    name = Column(String(30))
    colour = Column(String(30), nullable=True)
    exportable = Column(Boolean, nullable=True)

    def __str__(self):
        return f"{self.name} | {self.colour}"


class Indicator(IDBase, TimestampBase):
    """
    Модель индикатора.
    """
    __tablename__ = "indicator"

    type = Column(
        String(255), default=TypesEnum.IP.value, nullable=False, name="type"
    )
    uuid = Column(
        String(255), unique=True, name="uuid"
    )
    category = Column(
        String(128), nullable=True
    )

    value = Column(
        String(256)
    )

    weight = Column(
        Integer, CheckConstraint("weight > 0 AND age < 100"), default=0
    )

    tags = relationship(
        Tag, secondary="indicator_tag_m2m_table", backref="indicators"
    )

    false_detected = Column(
        Integer, CheckConstraint("false_detected > 0"), default=0
    )
    positive_detected = Column(
        Integer, CheckConstraint("positive_detected > 0"), default=0
    )
    detected = Column(
        Integer, CheckConstraint("detected > 0"), default=0
    )
    first_detected_date = Column(DateTime, nullable=True)
    last_detected_date = Column(DateTime, nullable=True)
    # Данные об источнике
    supplier_name = Column(String(128))
    supplier_vendor_name = Column(String(128))
    supplier_type = Column(String(64))
    supplier_confidence = Column(
        Integer, CheckConstraint("supplier_confidence > 0 AND supplier_confidence < 100"), default=0
    )
    supplier_created_date = Column(DateTime, nullable=True)
    # Контекст
    ioc_context_exploits_md5 = Column(String(64), nullable=True)
    ioc_context_exploits_sha1 = Column(String(64), nullable=True)
    ioc_context_exploits_sha256 = Column(String(64), nullable=True)
    ioc_context_exploits_threat = Column(String(64), nullable=True)
    ioc_context_av_verdict = Column(String(64), nullable=True)
    ioc_context_ip = Column(String(64), nullable=True)
    ioc_context_md5 = Column(String(64), nullable=True)
    ioc_context_sha1 = Column(String(64), nullable=True)
    ioc_context_sha256 = Column(String(64), nullable=True)
    ioc_context_affected_products_product = Column(String(64), nullable=True)

    joc_context_domains = Column(String(64), nullable=True)
    ioc_context_file_names = Column(String(64), nullable=True)
    ioc_context_file_size = Column(String(64), nullable=True)
    ioc_context_file_type = Column(String(64), nullable=True)
    ioc_context_files_behaviour = Column(String(64), nullable=True)
    ioc_context_files_md5 = Column(String(64), nullable=True)
    ioc_context_files_sha1 = Column(String(64), nullable=True)
    ioc_context_files_sha256 = Column(String(64), nullable=True)
    ioc_context_files_threat = Column(String(64), nullable=True)
    ioc_context_malware = Column(String(64), nullable=True)
    ioc_context_mask = Column(String(64), nullable=True)
    ioc_context_popularity = Column(String(64), nullable=True)
    ioc_context_port = Column(String(64), nullable=True)
    ioc_context_protocol = Column(String(64), nullable=True)
    ioc_context_publication_name = Column(String(64), nullable=True)

    ioc_context_severity = Column(String(64), nullable=True)
    ioc_context_type = Column(String(64), nullable=True)
    ioc_context_url = Column(String(64), nullable=True)
    ioc_context_urls_url = Column(String(64), nullable=True)
    ioc_context_vendors_vendor = Column(String(64), nullable=True)
    ioc_context_geo = Column(String(64), nullable=True)
    ioc_context_id = Column(String(64), nullable=True)
    ioc_context_industry = Column(String(64), nullable=True)
    ioc_context_ip = Column(String(64), nullable=True)
    ioc_context_ip_geo = Column(String(64), nullable=True)
    ioc_context_ip_whois_asn = Column(String(64), nullable=True)
    ioc_context_ip_whois_contact_abuse_country = Column(
        String(64), nullable=True)
    ioc_context_ip_whois_contact_abuse_email = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_contact_abuse_name = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_contact_owner_city = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_contact_owner_code = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_contact_owner_country = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_contact_owner_email = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_contact_owner_name = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_country = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_created = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_desrc = Column(String(64), nullable=True)
    ioc_context_ip_whois_net_name = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_net_range = Column(
        String(64), nullable=True
    )
    ioc_context_ip_whois_updated = Column(
        String(64), nullable=True
    )
    ioc_context_whois_mx = Column(String(64), nullable=True)
    ioc_context_whois_mx_ips = Column(String(64), nullable=True)
    ioc_context_whois_ns = Column(String(64), nullable=True)
    ioc_context_whois_ns_ips = Column(String(64), nullable=True)
    ioc_context_whois_city = Column(String(64), nullable=True)
    ioc_context_whois_country = Column(String(64), nullable=True)
    ioc_context_whois_created = Column(String(64), nullable=True)
    ioc_context_whois_domain = Column(String(64), nullable=True)
    ioc_context_whois_email = Column(String(64), nullable=True)
    ioc_context_whois_expires = Column(String(64), nullable=True)
    ioc_context_whois_name = Column(String(64), nullable=True)
    ioc_context_whois_org = Column(String(64), nullable=True)
    ioc_context_whois_registrar_email = Column(String(64), nullable=True)
    ioc_context_whois_registrar_name = Column(
        String(64), nullable=True
    )
    ioc_context_whois_updated = Column(String(64), nullable=True)

    # время жизни
    ttl = Column(DateTime, nullable=True, default=None)

    enrichment_context = Column(JSONB, default=None, nullable=True)

    push_to_detections = Column(Boolean, default=False)

    # false = false, true = positive
    false_or_positive = Column(Boolean, default=False)

    comment = Column(Text, default=None, nullable=True)

    is_archived = Column(Boolean, default=False, index=True)

    def __str__(self):
        return f"{self.value}"

    @classmethod
    def get_model_fields(cls):
        exclude = ('enrichment_context',)
        fields = {}
        for i in cls._meta.fields:
            if i.attname not in exclude:
                fields[i.attname] = list(i.class_lookups.keys())
        return fields


class FeedParsingRuleM2MTable(IDBase):
    __tablename__ = "feed_parsing_rule_m2m_table"

    parsing_rule_id = Column(
        Integer,
        ForeignKey("parsing_rule.id"),
        primary_key=True
    )
    feed_id = Column(
        Integer,
        ForeignKey("feed.id"),
        primary_key=True
    )


class FeedIndicatorM2MTable(IDBase):
    __tablename__ = "feed_indicator_m2m_table"

    feed_id = Column(
        Integer,
        ForeignKey("feed.id"),
        primary_key=True
    )
    indicator_id = Column(
        Integer,
        ForeignKey("indicator.id"),
        primary_key=True
    )


class ParsingRule(IDBase, TimestampBase):
    """
    Модель правила для парсинга (CSV)
    """
    __tablename__ = "parsing_rule"


class Feed(IDBase, TimestampBase):
    """
    Модель фида - источника данных.
    """

    __tablename__ = "feed"

    type_of_feed = Column(
        String(5), default=TypesEnum.IP.value,
        name="types"
    )
    format_of_feed = Column(
        String(5), default=FeedFormatEnum.TXT_FILE.value,
        name="format_of_feed"
    )
    auth_type = Column(
        String(5), default=AuthEnum.NO_AUTH.value,
        name="auth_type"
    )
    # polling_frequency = Column(
    #     Enum(PollingFrequencyEnum),
    #     default=PollingFrequencyEnum.NEVER,
    #     name="polling_frequency"
    # )

    auth_login = Column(
        String(32), nullable=True
    )
    auth_password = Column(
        String(64), nullable=True
    )
    auth_querystring = Column(
        String(128), nullable=True
    )
    separator = Column(
        String(8), nullable=True
    )
    parsing_rules = relationship(
        ParsingRule,
        secondary="feed_parsing_rule_m2m_table",
        backref="feeds"
    )
    custom_field = Column(
        String(128), nullable=True
    )
    sertificate_file_name = Column(String(50), nullable=True)
    sertificate = Column(LargeBinary, nullable=True)
    vendor = Column(String(32), default='Тестовый вендор')
    name = Column(String(32), unique=True)
    link = Column(String(255))
    confidence = Column(
        Integer, CheckConstraint("confidence > 0 AND confidence < 100"), default=0
    )
    records_quantity = Column(Integer, nullable=True)

    indicators = relationship(
        Indicator, backref="feeds", secondary="feed_indicator_m2m_table"
    )

    update_status = Column(
        Enum(StatusUpdateEnum), default=StatusUpdateEnum.ENABLED,
        name="update_status"
    )

    ts = Column(DateTime, default=func.now())

    source_id = Column(
        Integer, ForeignKey("source.id"), nullable=True, default=None,
        name='source_id'
    )

    modified = Column(DateTime, default=func.now())

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_model_fields(cls):
        return [i.attname for i in cls._meta.fields]

    @classmethod
    def create_feed(cls, data: dict):
        fields = tuple(cls.get_model_fields())
        feed = {}
        for key in data:
            if key in fields:
                feed[key] = data[key]
        return Feed(**feed)

    class Meta:
        verbose_name = "Фид"
        verbose_name_plural = "Фиды"


class Source(IDBase, TimestampBase):

    __tablename__ = "source"

    name = Column(String(255), unique=True)
    is_instead_full = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    provider_name = Column(String(255))
    path = Column(Text)
    certificate_file_name = Column(String(50), nullable=True)
    certificate = Column(LargeBinary, nullable=True)
    authenticity = Column(
        Integer, CheckConstraint("authenticity > 0 AND authenticity < 100"),
        default=0
    )
    format = Column(
        String(50), default=FormatTypeEnum.CSV.value,
        name="format"
    )

    auth_type = Column(
        String(50), default=AuthEnum.NO_AUTH.value,
        name="auth_type"
    )
    auth_login = Column(
        String(32), nullable=True
    )
    auth_password = Column(
        String(64), nullable=True
    )

    max_rows = Column(Integer, default=None, nullable=True)
    raw_indicators = Column(Text, default=None, nullable=True)
    update_time_period = Column(Integer, CheckConstraint(
        "update_time_period > 0"), default=0)

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'
