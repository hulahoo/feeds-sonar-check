import csv
import json

from abc import ABC, abstractmethod
from io import StringIO
from xml.etree import ElementTree
from jsonpath_ng import parse
from typing import Iterator

from feeds_importing_worker.apps.importer.utils import ParsingRules
from feeds_importing_worker.apps.models.models import Indicator


class IParser(ABC):
    @abstractmethod
    def get_indicators(self, data: str, parsing_rules: json) -> Iterator[Indicator]:
        pass


class PlainTextParser(IParser):
    def get_indicators(self, data: str, parsing_rules: json) -> Iterator[Indicator]:
        parsing_rules = ParsingRules(parsing_rules)

        for value in data:
            if not value or value[0] == '#':
                continue

            yield Indicator(
                ioc_type=parsing_rules['ioc-type'].value,
                value=value,
            )


class CSVParser(IParser):
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


class Stix2Parser(IParser):
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


class JsonParser(IParser):
    def get_indicators(self, data: str, parsing_rules: json) -> Iterator[Indicator]:
        content = ''

        for value in data:
            content += value

        indicators = json.loads(content)

        jsonpath_expression = parse(parsing_rules['prefix'])

        for match in jsonpath_expression.find(indicators):

            json_type = match.value[parsing_rules['ioc-type']]

            if json_type in parsing_rules['type_mapping']:
                yield Indicator(
                    ioc_type=parsing_rules['type_mapping'][json_type],
                    value=match.value[parsing_rules['ioc-value']],
                )


class Stix1Parser(IParser):
    TYPE_MAPPING = {
        'cyboxCommon:Simple_Hash_Value': 'hash',
        'DomainNameObj:Value': 'domain',
        'URIObj:Value': 'url',
        'AddressObj:Address_Value': 'ip',
    }

    def _get_ns(self, content):
        content_io = StringIO(content)
        events = "start", "start-ns"
        ns = {}

        for event, elem in ElementTree.iterparse(content_io, events):
            if event == "start-ns":
                ns[elem[0]] = "%s" % elem[1]

        return ns

    def get_indicators(self, data: str, parsing_rules: json = None) -> Iterator[Indicator]:
        content = ''

        for value in data:
            content += value

        root = ElementTree.fromstring(content)
        ns = self._get_ns(content)

        for element in root.findall(path='.//stix:Indicator', namespaces=ns):
            for selector in self.TYPE_MAPPING:
                for value in element.findall(path=f'.//{selector}', namespaces=ns):
                    yield Indicator(
                        ioc_type=self.TYPE_MAPPING[selector],
                        value=value.text,
                    )


class XMLParser(IParser):
    def get_indicators(self, data: str, parsing_rules: json) -> Iterator[Indicator]:
        content = ''

        for value in data:
            content += value

        root = ElementTree.fromstring(content)

        xmlns = root.tag.split('}')[0].strip('{')

        namespaces = {
            'xmlns': xmlns
        }

        for value in root.findall(path=f'.//xmlns:{parsing_rules["ioc-value"]}', namespaces=namespaces):
            yield Indicator(
                ioc_type=parsing_rules['ioc-type'],
                value=value.text,
            )
