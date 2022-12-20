import csv
import json

from xml.etree import ElementTree
from typing import Iterator

from feeds_importing_worker.apps.importer.utils import ParsingRules
from feeds_importing_worker.apps.models.models import Indicator


class PlainTextParser:
    def get_indicators(self, data: str, parsing_rules: json) -> Iterator[Indicator]:
        parsing_rules = ParsingRules(parsing_rules)

        for value in data:
            if not value or value[0] == '#':
                continue

            yield Indicator(
                ioc_type=parsing_rules['ioc-type'].value,
                value=value,
            )


class CSVParser:
    def get_indicators(self, data: str, parsing_rules: json) -> Iterator[Indicator]:
        parsing_rules = ParsingRules(parsing_rules)

        reader = csv.reader(data, delimiter=',')

        skip_header = True

        for row in reader:
            if not row[0] or row[0][0] == '#':
                continue

            if skip_header:
                skip_header = False
                continue

            context = {}
            for context_rule in parsing_rules.get_context_rules():
                context[context_rule] = row[parsing_rules[f'context.{context_rule}'].column]

            yield Indicator(
                ioc_type=parsing_rules['ioc-type'].value,
                value=row[parsing_rules['ioc-value'].column],
                context=context
            )


class Stix2Parser:
    TYPE_MAPPING = {
        'hashes': 'hash',
        'domain': 'domain',
        'url': 'url',
        'ipv4': 'ip',
        'email': 'email',
    }

    def _get_type(self, value: str):
        for pattern in self.TYPE_MAPPING:
            if value.find(pattern) != -1:
                return self.TYPE_MAPPING[pattern]

    def get_indicators(self, data: str, parsing_rules: json = None) -> Iterator[Indicator]:
        content = ''

        # TODO: сделать потоковый парсинг для больших файлов
        for value in data:
            content += value

        indicators = json.loads(content)

        for obj in indicators['objects']:
            if obj['type'] != 'indicator':
                continue

            pattern = obj['pattern'].strip('[').strip(']')

            stix_type, value = map(lambda item: item.strip().strip("'"), pattern.split('=', 1))

            yield Indicator(
                ioc_type=self._get_type(stix_type),
                value=value,
            )


class Stix1Parser:
    NAMESPACES = {
        'stix': 'http://stix.mitre.org/stix-1',
        'cyboxCommon': 'http://cybox.mitre.org/common-2',
        'DomainNameObj': 'http://cybox.mitre.org/objects#DomainNameObject-1',
        'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2"
    }

    TYPE_MAPPING = {
        'cyboxCommon:Simple_Hash_Value': 'hash',
        'DomainNameObj:Value': 'domain',
        'URIObj:Value': 'url',
        'AddressObj:Address_Value': 'ip',
    }

    def get_indicators(self, data: str, parsing_rules: json = None) -> Iterator[Indicator]:
        content = ''

        # TODO: сделать потоковый парсинг для больших файлов
        for value in data:
            content += value

        root = ElementTree.fromstring(content)

        for element in root.findall(path='.//stix:Indicator', namespaces=self.NAMESPACES):
            for selector in self.TYPE_MAPPING:
                for value in element.findall(path=f'.//{selector}', namespaces=self.NAMESPACES):
                    yield Indicator(
                        ioc_type=self.TYPE_MAPPING[selector],
                        value=value.text,
                    )
