#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import time
import datetime
import logging

from pytz import timezone
from django.conf import settings
from django.db import transaction

from .parser_config import *
from .data_provider import LogAdapterDataProvider
from .blacklist import LogAdapterBlacklistManager
from .representer import *


class LogAdapterEngine:
    logger = logging.getLogger(__name__)
    log_file = None
    data_provider = None
    blacklist_manager = None
    app_config = None
    mail_status_model = None

    def __init__(self, app_config):
        self.logger.info('initializing log adapter engine')
        self.app_config = app_config
        self.log_file = settings.POSTFIX_MAIL_FILE

        self.logger.info('connecting to data provider')
        self.data_provider = LogAdapterDataProvider(self.log_file, interval=1)

        self.logger.info('registering callback to data provider')
        self.data_provider.register_callback(self.process_line)

        self.logger.info('creating blacklist manager with default configuration')
        self.blacklist_manager = LogAdapterBlacklistManager()

        self.mail_status_model = self.app_config.get_model('MailStatus')

    def start(self):
        self.logger.info('starting log adapter engine')
        self.data_provider.start()
        self.logger.info('started log adapter engine')

        found = self.mail_status_model.objects.count()
        self.logger.info('found %d mail status records on DB', found)

    def stop(self):
        self.logger.info('stopping log adapter engine')
        self.data_provider.stop()
        self.logger.info('stopped log adapter engine')

    def extract_attribute(self, extraction, name):
        for token in extraction:
            if token.name == name:
                return token.value

    def process_line(self, line):
        if line is None or len(line) < 5:
            self.logger.info('skipping empty or near-empty line')
            return

        self.logger.debug('parsing line ' + line.strip() if line else 'empty line')

        if self.blacklist_manager.check_blacklist(line):
            self.logger.debug('line blacklisted')
            return

        for parser in parsers:
            if parser.prematch(line):
                result = parser.extract(line)
                if parser.validate(line, result):
                    self.apply_line(line, result)
                    break
                else:
                    self.logger.error('EXTRACTION RESULT INVALIDATED')

    @transaction.atomic
    def apply_line(self, line, extraction):
        log_line_extraction(extraction)
        queue_id = self.extract_attribute(extraction, 'queue_id')
        self.logger.info('applying line event to queue id %s', queue_id)

        mail_status = self.find_or_create(queue_id)

        self.add_event(mail_status, extraction)
        self.aggregate_attributes(mail_status, extraction)

        log_mail_status(mail_status)

    def find_or_create(self, queue_id):
        mail_status = self.mail_status_model.manager.by_queue_id(queue_id)

        if mail_status:
            self.logger.debug('queue id is known already with ID %d', mail_status.id)
        else:
            mail_status = self.mail_status_model.manager.create(queue_id, status='pending')
            self.logger.info('instantiated new mail status entry for mail %s with ID %d', queue_id, mail_status.id)
        return mail_status

    def add_event(self, mail_status, extraction):
        self.logger.debug('adding new event record')

        creation_ts = self.extract_attribute(extraction, 'timestamp')
        self.logger.info('new record timestamp is %s', creation_ts)
        
        event = mail_status.events.create(event_date=creation_ts)

        self.logger.debug('created event with ID %d', event.id)

        for token in extraction:
            if token.name == 'status':
                event.status = token.value
            elif token.name == 'host_message':
                event.message = token.value
            elif token.name == 'event':
                event.event = token.value

            attribute = event.attributes.create(
                name=token.name, 
                value=str(token.value), 
                confidence=token.confidence,
                aggregate=token.aggregate )
            self.logger.debug('created event attribute with ID %d', attribute.id)

        event.save()
        return event

    def aggregate_attributes(self, mail_status, extraction):
        self.logger.debug('aggregating record attributes')

        mail_status_attributes = mail_status.attributes.all()
        len(mail_status_attributes) # force loading

        known_attributes = [attribute.name for attribute in mail_status_attributes]

        for token in [t for t in extraction if t.aggregate]:
            if token.name == 'message_id':
                mail_status.message_id = token.value
            elif token.name == 'status':
                mail_status.status = token.value
            elif token.name == 'host_message':
                mail_status.message = token.value

            if token.name not in known_attributes:
                self.logger.debug('attribute \'%s\' is new for mail \'%s\'', token.name, mail_status.id)
                new_attribute = mail_status.attributes.create(
                    name=token.name,
                    value=str(token.value),
                    confidence=token.confidence,
                    aggregate=token.aggregate
                )
                self.logger.debug('attribute created with ID %d', new_attribute.id)
            else:
                current_attribute = next((attr for attr in mail_status_attributes if attr.name == token.name), None)
                self.logger.debug('attribute \'%s\' is already known for mail %s with ID %d', token.name, mail_status.id, current_attribute.id)

                if token.confidence >= current_attribute.confidence:
                    self.logger.debug('incoming attribute \'%s\' has higher confidence for mail \'%s\' and will replace current attribute', token.name, mail_status.id)
                    current_attribute.value = token.value
                    current_attribute.confidence = token.confidence
                    current_attribute.aggregate = token.aggregate
                    current_attribute.version += 1
                    current_attribute.save()
                else:
                    self.logger.debug('incoming attribute \'%s\' has lower confidence for mail \'%s\' and will be discarded', token.name, mail_status.id)

        mail_status.version += 1
        mail_status.save()