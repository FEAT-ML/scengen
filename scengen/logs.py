# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import logging as pylog
from enum import Enum
from pathlib import Path
from typing import NoReturn, Optional, List


class LogLevel(Enum):
    """Levels for Logging"""

    PRINT = 100
    CRITICAL = pylog.CRITICAL
    ERROR = pylog.ERROR
    WARN = pylog.WARNING
    WARNING = pylog.WARNING
    INFO = pylog.INFO
    DEBUG = pylog.DEBUG


_loggers: List[pylog.Logger] = []
_handlers: List[pylog.Handler] = []

_FORMAT_NORMAL = "%(asctime)s — %(levelname)s — %(message)s"  # noqa
_FORMAT_DETAILLED = "%(asctime)s.%(msecs)03d — %(levelname)s — %(module)s:%(funcName)s:%(lineno)d — %(message)s"  # noqa
_TIME_FORMAT = "%H:%M:%S"

_INFO_UPDATING_LOG_LEVEL = "Updating scengen log level to: {}"
_WARN_NOT_INITIALIZED = "Logger for scengen not initialised: using default log level `WARNING`"

LOGGER_NAME = "scengen"
DEFAULT_LOG_LEVEL = LogLevel.WARNING


def log() -> pylog.Logger:
    """Returns already set up scengen's logger or - if not set up - a new logger with level `WARNING`"""
    if not _loggers:
        scengen_logger(DEFAULT_LOG_LEVEL.name)
        pylog.warning(_WARN_NOT_INITIALIZED)
    return _loggers[0]


def log_and_raise_critical(message: str) -> NoReturn:
    """Raises a critical error and logs with given `error_message`"""
    log().critical(message)
    raise Exception(message)


def log_error_and_raise(exception: Exception) -> NoReturn:
    """Raises the specified `exception` and logs an error with the same `message`"""
    log().error(str(exception))
    raise exception


def scengen_logger(log_level_name: str, file_name: Optional[Path] = None) -> None:
    """
    Ensures a logger for scengen is present and uses the specified options

    Args:
        log_level_name: one of Python's official logging level names, e.g. "INFO"
        file_name: if present, logs are also written to the specified file path
    """
    log_level = LogLevel[log_level_name.upper()]
    logger = _get_logger(log_level)

    formatter = _get_formatter(log_level)
    _add_handler(logger, pylog.StreamHandler(), formatter)
    if file_name:
        _add_handler(logger, pylog.FileHandler(file_name, mode="w"), formatter)

    if _loggers:
        pylog.info(_INFO_UPDATING_LOG_LEVEL.format(log_level_name))
        _loggers[0] = logger
    else:
        _loggers.append(logger)


def _get_logger(level: LogLevel) -> pylog.Logger:
    """
    Returns scengen logger with given log level without any handler and, not propagating to parent

    Args:
        level: integer representing the log level

    Returns:
        logger for scengen with specified level
    """
    logger = pylog.getLogger(LOGGER_NAME)
    logger.setLevel(level.value)
    logger.propagate = False
    for handler in _handlers:
        logger.removeHandler(handler)
    _handlers.clear()
    return logger


def _get_formatter(level: LogLevel) -> pylog.Formatter:
    """
    Returns a log formatter depending on the given log `level`
    Args:
        level: this log level determines how detailed the logger's output is
    Returns:
        new log formatter
    """
    return pylog.Formatter(_FORMAT_DETAILLED if level is LogLevel.DEBUG else _FORMAT_NORMAL, _TIME_FORMAT)


def _add_handler(logger: pylog.Logger, handler: pylog.Handler, formatter: pylog.Formatter) -> None:
    """Adds given `handler` using the specified `formatter` to given `logger` and `_handlers` list"""
    handler.setFormatter(formatter)
    _handlers.append(handler)
    logger.addHandler(handler)
