#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging


def log_line_extraction(result):
    for token in result:
        logging.info('%s = %s, %s', token.name, token.value, 'not-aggregable' if not token.aggregate else 'confidence ' + str(token.confidence))


def log_mail_status(mail_status):
    logging.info('-' * 80)
    logging.info('| mail status for %s', mail_status.queue_id)
    logging.info('| ')
    logging.info('| attributes:')
    for token in mail_status.attributes.all():
        logging.info('|\t%s = %s, %s', token.name, token.value, 'not-aggregable' if not token.aggregate else 'confidence ' + str(token.confidence))
    logging.info('| ')
    logging.info('| events:')
    for event in mail_status.events.all():
        logging.info('| \tevent # %d', event.id)
        for t in event.attributes.all():
            logging.info('| \t\t%s = %s', t.name, str(t.value))
    logging.info('-' * 80)
