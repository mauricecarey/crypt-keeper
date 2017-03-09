from logging import StreamHandler, Formatter, getLogger
from django.conf import settings

# setup logging for root logger.
__console_handler = StreamHandler()
__console_handler.setLevel(settings.LOG_LEVEL)

__formatter = Formatter(settings.LOG_FORMAT)
__console_handler.setFormatter(__formatter)

log = getLogger()
log.addHandler(__console_handler)
