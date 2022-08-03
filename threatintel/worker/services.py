from intelhandler.script import parse_custom_json, parse_stix, parse_free_text, parse_misp, parse_csv

methods = {
    "json": parse_custom_json,
    "stix": parse_stix,
    "free_text": parse_free_text,
    "misp": parse_misp,
    "csv": parse_csv,
    "txt":parse_free_text
}


def choose_type(name: str):
    return methods[name]
