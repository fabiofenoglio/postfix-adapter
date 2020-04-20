#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import time
import datetime
import logging

from pytz import timezone

from .parser_model import *

CONFIDENCE_TOP = 100
CONFIDENCE_LOW = 10

SERVER_TIMEZONE = timezone('Europe/Rome')

common_extractor = Extractor(
    '(?P<timestamp>\w+\s+\d{1,2}\s+\d{1,2}\:\d{1,2}\:\d{1,2})\s+(?P<host>[\w\-\.]+)\s+' +
    '(?P<process>postfix\/\w+)\[\d+\]\s*\:\s*(?P<queueid>[\da-fA-F]+)\s*\:\s*',
    [   ExtractorToken('timestamp', CONFIDENCE_TOP, aggregate=False, parser=lambda raw:
            SERVER_TIMEZONE.localize( 
                datetime.datetime.strptime(datetime.datetime.now().strftime('%Y ') + raw, '%Y %b %d %H:%M:%S'))), 
        ExtractorToken('host', CONFIDENCE_TOP, aggregate=False),
        ExtractorToken('process', CONFIDENCE_TOP, aggregate=False), 
        ExtractorToken('queueid', CONFIDENCE_TOP, aggregate=False, alias='queue_id') ] )


parsers = [ 
    RowParser(
        ["/cleanup[", "message-id="], 
        [common_extractor, 
        Extractor('message\\-id=\\s*(?P<messageid>[^\\s]+)', [ExtractorToken('messageid', CONFIDENCE_TOP, alias='message_id')]),
        Extractor(None, [ExtractorToken('event', CONFIDENCE_TOP, value='RECEIVED', aggregate=False)])
        ] ),
    RowParser(
        ["/smtpd[", "client=", "sasl_username"], 
        [common_extractor, 
        Extractor('(?<=client=)(?P<client>.*?)(?=[,\\r\\n])', [ExtractorToken('client', CONFIDENCE_TOP)]),
        Extractor('sasl_username=\s*(?P<saslusername>.*)', [ExtractorToken('saslusername', CONFIDENCE_TOP, alias='sasl_username')]),
        Extractor(None, [ExtractorToken('event', CONFIDENCE_TOP, value='AUTHENTICATED', aggregate=False)]) ] ),
    RowParser(
        ["/cleanup[", "warning:", "header Subject:", "from=<", "to=<"], 
        [common_extractor, 
        Extractor('(?<=Subject: )(?P<subject>.*?)(?=\\sfrom)', [ExtractorToken('subject', CONFIDENCE_TOP)]),
        Extractor('(?<=from=<)(?P<from>.*?)(?=>)', [ExtractorToken('from', CONFIDENCE_LOW)]),
        Extractor('(?<=to=<)(?P<to>.*?)(?=>)', [ExtractorToken('to', CONFIDENCE_LOW)]),
        Extractor(None, [ExtractorToken('event', CONFIDENCE_TOP, value='PARSED', aggregate=False)]) ] ),
    RowParser(
        ["/qmgr[", "from=<", "size=", "nrcpt="], 
        [common_extractor, 
        Extractor('(?<=from=<)(?P<from>.*?)(?=>)', [ExtractorToken('from', CONFIDENCE_TOP)]),
        Extractor(None, [ExtractorToken('event', CONFIDENCE_TOP, value='ENQUEUED', aggregate=False)])] ),
    RowParser(
        ["/smtp[", "to=<", "relay=", "delay=", "delays=", "dsn=", "status="], 
        [common_extractor, 
        Extractor('(?<=to=<)(?P<to>.*?)(?=>)', [ExtractorToken('to', CONFIDENCE_TOP)]),
        Extractor('(?<=relay=)(?P<relay>.*?)(?=,\\s+delay)', [ExtractorToken('relay', CONFIDENCE_TOP)]),
        Extractor('(?<=delay=)(?P<delay>.*?)(?=,\\s+delays)', [ExtractorToken('delay', CONFIDENCE_TOP)]),
        Extractor('(?<=delays=)(?P<delays>.*?)(?=,\\s+dsn)', [ExtractorToken('delays', CONFIDENCE_TOP)]),
        Extractor('(?<=dsn=)(?P<dsn>.*?)(?=,\\s+status)', [ExtractorToken('dsn', CONFIDENCE_TOP)]),
        Extractor('(?<=status=)(?P<status>.*?)(?=\\s)', [ExtractorToken('status', CONFIDENCE_TOP)]),
        Extractor('status=(?P<status>[^\\s]+)\\s*\\((?P<statuscode>[\\d]+\\s*)\\s+(?P<hostmessage>.*)\\)\\s*', [ExtractorToken('statuscode', CONFIDENCE_TOP, alias='status_code', optional=True)]),
        Extractor('status=(?P<status>[^\\s]+)\\s*\\((?P<hostmessage>.*)\\)\\s*', [ExtractorToken('hostmessage', CONFIDENCE_TOP, alias='host_message')]),
        Extractor(None, [ExtractorToken('event', CONFIDENCE_TOP, value='DELIVERY_ATTEMPT', aggregate=False)]) ] ),
    RowParser(
        ["/qmgr[", ": removed"], 
        [common_extractor, 
        Extractor('\\: (?P<removedmarker>removed)\\s*[$\\r\\n]*', [ExtractorToken('removedmarker', CONFIDENCE_TOP, alias='removed_marker', value=True)]),
        Extractor(None, [ExtractorToken('event', CONFIDENCE_TOP, value='REMOVED', aggregate=False)]) ] )
]
