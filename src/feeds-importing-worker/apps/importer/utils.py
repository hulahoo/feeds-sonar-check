from typing import Iterator
import json
import re


class ParsingRule:
    def __init__(self, parsing_rule: str):
        self.parsing_rule = parsing_rule

    @property
    def value(self) -> str:
        if self.parsing_rule[0] == '%':
            return ''

        return self.parsing_rule

    @property
    def column(self) -> int:
        match = re.search('%COL-(.+)%', self.parsing_rule)

        return int(match.group(1))


class ParsingRules:
    def __init__(self, parsing_rules: json):
        self.parsing_rules = parsing_rules

    def __getitem__(self, item) -> ParsingRule:
        return ParsingRule(self.parsing_rules[item])

    def get_context_rules(self) -> Iterator[str]:
        for rule in self.parsing_rules:
            match = re.search('context\\.(.+)', rule)

            if not match:
                continue

            for group in match.groups():
                yield group
