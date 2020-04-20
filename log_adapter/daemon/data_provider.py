#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import time
import datetime
import logging
from threading import Thread


class LogAdapterDataProvider:
    logger = logging.getLogger(__name__)
    log_file = '/var/log/mail.log'
    tailing = False
    seek_end = True
    callback = None
    interval = None

    thread = None
    connected = False
    shutdown = False

    def __init__(self, log_file, callback=None, interval=1):
        self.logger.info('initializing log adapter data provider')
        if log_file:
            self.log_file = log_file
        self.callback = callback
        self.interval = interval

    def register_callback(self, callback):
        self.callback = callback

    def start(self):
        self.thread = Thread(target = self.connect_threaded)
        self.thread.start()
        return self.thread

    def connect_threaded(self):
        logger = logging.getLogger(__name__ + '-instance')
        logger.info('connecting data provider to file source %s', self.log_file)
        self.tailing = False
        self.seek_end = True

        while not self.shutdown:  # handle moved/truncated files by allowing to reopen
            with open(self.log_file) as f:
                logger.info('input file opened')
                self.connected = True
                if self.seek_end:  # reopened files must not seek end
                    logger.info('input file seeking to 0, 2')
                    f.seek(0, 2)
                while not self.shutdown:  # line reading loop
                    line = f.readline()
                    if not line:
                        try:
                            if f.tell() > os.path.getsize(self.log_file):
                                logger.info('input file rotation occured')
                                # rotation occurred (copytruncate/create)
                                f.close()
                                self.seek_end = False
                                break
                        except FileNotFoundError:
                            # rotation occurred but new file still not created
                            pass  # wait and retry
                        time.sleep(self.interval)
                    else:
                        logger.debug('input file has new line')
                        self.process_line(line)

        self.connected = False

    def process_line(self, line):
        if self.callback:
            self.callback(line)

    def stop(self):
        self.logger.info("requesting thread shutdown")
        self.shutdown = True
        self.logger.info("thread shutdown requested, waiting")
        self.thread.join()
        self.logger.info("thread shutdown completed")