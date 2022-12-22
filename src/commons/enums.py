from enum import Enum


class TypesEnum(Enum):
    EMAIL_FROM: str = "FEMA"
    EMAIL_SUBJECT: str = "SEMA"
    MD5_HASH: str = "MD5H"
    SHA1_HASH: str = "SHA1"
    SHA256_HASH: str = "SHA2"
    IP: str = "IPAD"
    URL: str = "URLS"
    DOMAIN: str = "DOMN"
    FILENAME: str = "FILE"
    REGISTRY: str = "REGS"


class FeedFormatEnum(Enum):
    CSV_FILE: str = "CSV"
    JSON_FILE: str = "JSON"
    XML_FILE: str = "XML"
    TXT_FILE: str = "TXT"


class AuthEnum(Enum):
    NO_AUTH = "NAU"
    API = "API"
    BASIC = "BSC"


class PollingFrequencyEnum(Enum):
    NEVER = "NVR"
    THIRTY_MINUTES = "M30"
    ONE_HOUR = "HR1"
    TWO_HOURS = "HR2"
    FOUR_HOURS = "HR4"
    EIGHT_HOURS = "HR8"
    SIXTEEN_HOURS = "H16"
    TWENTY_FOUR_HOURS = "H24"


class StatusUpdateEnum(Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UPDATE_ERROR = "UPDATE_ERROR"


class FormatTypeEnum(Enum):
    STIX = "STIX"
    MISP = "MISP"
    FREE_TEXT = "FREE_TEXT"
    JSON = "JSON"
    CSV = "CSV"
