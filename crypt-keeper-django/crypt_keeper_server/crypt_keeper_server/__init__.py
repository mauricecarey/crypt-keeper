from logging import StreamHandler, Formatter, getLogger
from .configuration import CONFIGURATION
from .settings import LOG_LEVEL_DEFAULT

# setup logging for roor logger.
__console_handler = StreamHandler()
__console_handler.setLevel(CONFIGURATION.lookup('log:level', LOG_LEVEL_DEFAULT))

__formatter = Formatter(CONFIGURATION.lookup('log:format',
                                                     '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
__console_handler.setFormatter(__formatter)

log = getLogger()
log.addHandler(__console_handler)
