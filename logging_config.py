import logging
import os

LOG_FOLDER_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "./py-logs.log")

from logging.config import dictConfig

# new dict 27/1/20
DEFAULT_LOGGING = {
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'file': {'class': 'logging.handlers.RotatingFileHandler',
                          'filename': LOG_FOLDER_PATH,
                          'maxBytes': 100240,
                          'backupCount': 3,
                          'formatter': 'default'
                          }

                 },
    'loggers': {
        '': {  # root logger
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}

logging.config.dictConfig(DEFAULT_LOGGING)
# Get the logger specified in the file
