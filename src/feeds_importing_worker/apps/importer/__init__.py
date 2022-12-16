from .parser import CSVParser, PlainTextParser, Stix2Parser


def get_parser(format: str):
    if format == 'txt':
        return PlainTextParser()
    elif format == 'csv':
        return CSVParser()
    elif format == 'stix2':
        return Stix2Parser()
    else:
        raise Exception(f'Unknown format {format}')
