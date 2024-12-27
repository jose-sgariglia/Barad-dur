import os
import logging, time
from typing import ClassVar

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').disabled = True

# ---------------------
#    Code by akiidjk
# ---------------------

logger = logging.getLogger("barad_logger")

LOGS_DIR = "./logs/barad_{time}.log"


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"
    COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format_log_record = (
            f"{self.black}{self.bold}{{asctime}}{self.reset} "
            f"{log_color}{{levelname:<8}}{self.reset} "
            f"{self.green}{self.bold}{{name}}{self.reset} "
            f"{{message}}"
        )
        formatter = logging.Formatter(format_log_record, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


def init_logger(level: int):
    logger.setLevel(level)

    filelog_name = LOGS_DIR.format(time=time.strftime("%Y-%m-%d_%H:%M:%S"))
    os.makedirs(os.path.dirname(filelog_name), exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LoggingFormatter())
    # File handler
    file_handler = logging.FileHandler(filename=LOGS_DIR.format(time=time.strftime("%Y-%m-%d_%H:%M:%S")), encoding="utf-8", mode="w")
    file_handler_formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
    file_handler.setFormatter(file_handler_formatter)

    # Add the handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)