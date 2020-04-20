import re
import os
import sys
import time
import datetime
import logging

class RowParser:
    prematch_tokens = None
    extractors = []
    def __init__(self, prematch_tokens, extractors):
        self.prematch_tokens = prematch_tokens
        self.extractors = extractors

    def prematch(self, line):
        if line is not None:
            line = line.strip()
        logging.debug('running prematch on line [%s] with tokens %s', line, self.prematch_tokens)
        if self.prematch_tokens is None:
            logging.debug('no prematch phase for parser, prematch bypassed')
            return True
        if len(self.prematch_tokens) < 1:
            logging.warn('no prematch tokens for parser, prematch FAILED')
            return False
        for token in self.prematch_tokens:
            logging.debug('checking prematch token %s', token)
            if not token in line:
                logging.debug('missing prematch token %s, prematch is negative', token)
                return False
        logging.debug('all prematch tokens found, prematch is positive')
        return True

    def extract(self, line):
        out = []
        for extractor in self.extractors:
            cleaned_line = extractor.clean(line)
            if extractor.pattern:
                logging.debug('running token extraction with regex %s on line [%s]', extractor.regex, cleaned_line)
                match_result = re.search(extractor.pattern, cleaned_line)
                if match_result is None:
                    logging.debug('no matches for extractor')
                    continue
                for token in extractor.tokens:
                    extracted_value = match_result.group(token.name)
                    if extracted_value:
                        resolved_name = token.alias if token.alias is not None else token.name
                        if token.value:
                            logging.debug('replacing extracted raw value [%s] with token fixed value [%s]', extracted_value, token.value)
                            extracted_value = token.value
                        if token.parser:
                            logging.debug('running token parser on raw value [%s]', extracted_value)
                            extracted_value = token.parser(extracted_value)
                            logging.debug('processed token with parser on raw value with result [%s]', extracted_value)

                        logging.debug('found match with name %s in extractor matches, value is %s with confidence %s', resolved_name, extracted_value, token.confidence)
                        out.append(ExtractionResult(resolved_name, extracted_value, token.confidence, aggregate=token.aggregate))
                    else:
                        logging.debug('no match with name %s in extractor matches', token.name)
            else:
                logging.debug('running token extraction for extractor without a regex on line [%s]', cleaned_line)
                for token in extractor.tokens:
                    extracted_value = token.value
                    if token.parser:
                        logging.debug('running token parser on fixed value [%s]', extracted_value)
                        extracted_value = token.parser(extracted_value)
                        logging.debug('processed token with parser on fixed value with result [%s]', extracted_value)
                    resolved_name = token.alias if token.alias is not None else token.name
                    logging.debug('found value with name %s in extractor provided value %s with confidence %s', resolved_name, extracted_value, token.confidence)
                    out.append(ExtractionResult(resolved_name, extracted_value, token.confidence, aggregate=token.aggregate))

        return out

    def validate(self, line, extraction):
        logging.debug('running validation on extractor with %s results', len(extraction))
        num = 0
        for extractor in self.extractors:
            for token in extractor.tokens:
                if not token.optional:
                    num += 1

        logging.debug('expected %s results from extraction', num)
        if len(extraction) >= num:
            logging.debug('validation passed')
            return True
        else:
            logging.warn('extractor invalidated because of %s results instead of %s expected', len(extraction), num)
            for token in extraction:
                logging.debug('extracted %s', token.name)
            for extractor in self.extractors:
                for token in extractor.tokens:
                    logging.debug('expected %s', token.name)
            return False


class Extractor:
    regex = None
    pattern = None
    tokens = []
    def __init__(self, regex, tokens):
        self.regex = regex
        self.tokens = tokens
        if regex is not None:
            self.pattern = re.compile(regex)

    def clean(self, line):
        if line is None:
            return line
        return line.strip()


class ExtractorToken:
    name = None
    alias = None
    parser = None
    confidence = 0
    aggregate = True
    value = None
    optional = False
    def __init__(self, name, confidence, alias=None, parser=None, aggregate=True, value=None, optional = False):
        self.name = name
        self.alias = alias
        self.confidence = confidence
        self.parser = parser
        self.aggregate = aggregate
        self.value = value
        self.optional = optional


class ExtractionResult:
    name = None
    value = None
    confidence = 0
    aggregate = True
    def __init__(self, name, value, confidence, aggregate=True):
        self.name = name
        self.value = value
        self.confidence = confidence
        self.aggregate = aggregate