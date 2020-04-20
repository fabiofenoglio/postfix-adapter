#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import time
import datetime
import logging


DEFAULT_BLACKLIST = [["/smtpd[", "connect from"], ["SASL LOGIN authentication failed"], ["/smtpd[", "does not resolve to"]]

class LogAdapterBlacklistManager:
    logger = logging.getLogger(__name__)
    blacklist_registry = []

    def __init__(self, registry=None):
        if registry:
            self.logger.info('initializing blacklist manager with custom registry')
            self.blacklist_registry = registry
        else:
            self.logger.info('initializing blacklist manager with default registry')
            self.blacklist_registry = DEFAULT_BLACKLIST

    def check_blacklist(self, line):
        self.logger.debug('checking blacklisting for line')
        for tokens in self.blacklist_registry:
            matches = True
            for token in tokens:
                if not token in line:
                    matches = False
                    break
            if matches:
                return True
        return False
