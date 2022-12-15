import csv
import json

from typing import Iterator

from apps.importer.utils import ParsingRules
from apps.models.models import Indicator


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
