import logging
import sys
from django.apps import AppConfig, apps
from .daemon.runner import LogAdapterRunner


class LogAdapterConfig(AppConfig):
    logger = logging.getLogger(__name__)
    name = 'log_adapter'

    def ready(self):
        self.logger.info('application READY')

        if 'runserver' in sys.argv:
            self.logger.info('running in local development context')
            self.start_log_adapter_daemon()
        elif 'manage.py' in sys.argv:
            self.logger.info('running in manage.py context')
        else:
            self.logger.info('running in PRODUCTION context')
            self.start_log_adapter_daemon()

    def start_log_adapter_daemon(self):
        self.daemon_runner = LogAdapterRunner(self)
        self.daemon_runner.start()