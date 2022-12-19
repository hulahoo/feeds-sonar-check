from feeds_importing_worker.apps.importer.parser import CSVParser, PlainTextParser, Stix2Parser, Stix1Parser


def get_parser(format: str):
    if format == 'txt':
        return PlainTextParser()
    elif format == 'csv':
        return CSVParser()
    elif format == 'stix2':
        return Stix2Parser()
    elif format == 'stix1':
        return Stix1Parser()
    else:
        raise TypeError(f'Unknown format {format}')
