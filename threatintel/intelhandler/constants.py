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

ENABLED = "ENABLED"
DISABLED = "DISABLED"
UPDATE_ERROR = "UPDATE_ERROR"

TYPE_OF_STATUS_UPDATE = [
    (ENABLED, "ENABLED"),
    (DISABLED, "DISABLED"),
    (UPDATE_ERROR, "UPDATE_ERROR"),
]

STIX = "STIX"
MISP = "MISP"
FREE_TEXT = "FREE_TEXT"
JSON = "JSON"
CSV = "CSV"

TYPE_OF_FORMAT = [
    (STIX, "stix"),
    (MISP, 'misp'),
    (FREE_TEXT, 'free_text'),
    (JSON, "json"),
    (CSV, 'csv'),
]
