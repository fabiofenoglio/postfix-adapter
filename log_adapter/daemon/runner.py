#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import time
import datetime
import logging
import signal

from threading import Thread

from django.apps import apps

from .engine import LogAdapterEngine


class LogAdapterRunner:
    logger = logging.getLogger(__name__)
    thread_logger = logging.getLogger(__name__ + '-instance')
    engine = None
    shutdown = False
    thread = None
    app_config = None

    def __init__(self, app_config):
        self.logger.info('initializing log adapter runner')
        self.app_config = app_config
        self.engine = LogAdapterEngine(self.app_config)

    def start(self):
        self.logger.info('running log adapter engine from runner')
        self.thread = Thread(target = self.start_threaded)
        self.thread.start()

        # SIGINT for Ctrl+C
        # QUIT, INT: Quick shutdown for WSGI
        # TERM: Graceful shutdown for WSGI
        signal.signal(signal.SIGINT, self.sigint_handler_sigint)
        signal.signal(signal.SIGTERM, self.sigint_handler_sigterm)

        return self.thread

    def sigint_handler_sigint(self, signum, frame):
        print('SIGINT')
        if self.shutdown:
            self.logger.info('received SIGINT but runner stopped already')
        else:
            self.stop_for_signal()

    def sigint_handler_sigterm(self, signum, frame):
        print('SIGTERM')
        if self.shutdown:
            self.logger.info('received SIGTERM but runner stopped already')
        else:
            self.stop_for_signal()

    def stop_for_signal(self):
        self.logger.info('stopping instance because of signal')
        self.stop()
        self.logger.info('stopped instance after signal')
        sys.exit(0)

    def wait_django(self):
        self.thread_logger.info('waiting for django container app ...')
        while not apps.ready:
            self.thread_logger.debug('django container app is still not ready. waiting ...')
            time.sleep(0.2)
        self.thread_logger.info('django container app is now ready')

    def start_threaded(self):
        self.wait_django()

        self.thread_logger.info('starting engine in threaded instance')
        self.engine.start()
        
        while not self.shutdown:
            time.sleep(1)

        self.thread_logger.info('finished running engine in threaded instance')

        self.thread_logger.info('stopping engine in threaded runner instance')
        self.engine.stop()
        self.thread_logger.info('stopped engine in threaded runner instance')

    def stop(self):
       self.logger.info('stopping instance from runner')
       self.shutdown = True
       self.thread.join()
       self.logger.info('stopped instance from runner')