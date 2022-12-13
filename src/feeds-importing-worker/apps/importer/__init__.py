from .parser import CSVParser, PlainTextParser


def get_parser(format: str):
    if format == 'txt':
        return PlainTextParser()
    elif format == 'csv':
        return CSVParser()
    else:
        raise Exception(f'Unknown format {format}')
