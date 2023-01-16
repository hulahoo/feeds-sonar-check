from feeds_importing_worker.apps.importer.parser import (
    IParser, CSVParser, PlainTextParser, Stix2Parser, JsonParser, Stix1Parser, XMLParser
)


def get_parser(format: str) -> IParser:
    if format == 'txt':
        return PlainTextParser()
    elif format == 'csv':
        return CSVParser()
    elif format == 'stix2':
        return Stix2Parser()
    elif format == 'json':
        return JsonParser()
    elif format == 'stix1':
        return Stix1Parser()
    elif format == 'xml':
        return XMLParser()
    else:
        raise TypeError(f'Unknown format {format}')
