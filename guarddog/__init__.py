import sys as _sys

from loguru import logger as _logger

from guarddog.config import config as _config

_logger.remove()
_logger.add(_sys.stdout, colorize=True, format="[<green>{time:MM/DD/YYYY HH:mm:ss}</green>] <level>{message}</level>", level="INFO")
_logger.add("logs/errors_{time}.log", format="[{time}] {level}: {message}", level="ERROR", backtrace=True, diagnose=True, rotation="5 MB", compression="gz")
if _config.getboolean('Server', 'DevMode', fallback=False):
    _logger.add(_sys.stdout,
                colorize=True,
                format="<green>{time:MM/DD/YYYY HH:mm:ss}</green> <red>|</red> <level>{level}</level> <red>|</red> <cyan>{name}</cyan><red>:</red>{function}<red>:</red><cyan>{line}</cyan> <red>-</red> <level>{message}</level>",
                level="DEBUG",
                filter=lambda r: r['level'].name == "DEBUG")

