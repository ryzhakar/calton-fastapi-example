def construct_logging_config(
    level: str,
    app_name: str,
    log_format: str,
) -> dict:
    """Construct logging configuration."""
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': (
                    '%(asctime)s %(name)s %(log_color)s%(levelname)s '
                    '%(message)s'
                ),
                'datefmt': '[%Y-%m-%d %H:%M:%S]',
                'log_colors': {
                    'DEBUG': 'white',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bg_red',
                },
            },
            'json': {
                'format': (
                    '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s","app_name":'  # noqa: E501
                    f' "{app_name}"}}'
                ),
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'default': {
                'level': level,
                'formatter': log_format,
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'uvicorn': {
                'handlers': ['default'],
                'level': level,
                'propagate': False,
            },
            'app': {
                'handlers': ['default'],
                'level': level,
                'propagate': False,
            },
        },
    }
