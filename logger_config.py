import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

DEBUG_MODE = True# ⬅️ Altere para True quando quiser ver tudo

logger = logging.getLogger("chatbot_logger")
# Nível do logger ajustável
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.WARNING)

file_formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class RedWarningErrorFormatter(logging.Formatter):
    RED = "\033[31m"      # ANSI vermelho
    RESET = "\033[0m"

    def format(self, record):
        msg = super().format(record)
        if record.levelno in (logging.WARNING, logging.ERROR):
            return f"{self.RED}{msg}{self.RESET}"
        return msg

console_formatter = RedWarningErrorFormatter(
    "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logger.level)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5)
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logger.level)

if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

