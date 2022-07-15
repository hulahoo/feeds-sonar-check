from intelhandler.script import parse_custom_json, parse_stix, parse_free_text, convert_misp_to_indicator, parse_csv

methods = {
    "json":parse_custom_json,
    "stix":parse_stix,
    "free_text":parse_free_text,
    "misp":convert_misp_to_indicator,
    "csv":parse_csv
}

def choose_type(name:str):
    return methods[name]
