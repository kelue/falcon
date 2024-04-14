import logging
import os
import datetime
from logging.handlers import TimedRotatingFileHandler

# Create logs directory if it doesn't exist
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler - Rotates daily 
file_handler = TimedRotatingFileHandler(
    os.path.join(log_directory, "app_{}.log".format(datetime.date.today())),
    when="D",  # D stands for daily rotation 
    interval=1, 
    backupCount=7  # Keep up to 7 days of logs
)
file_handler.setLevel(logging.WARNING)

console_handler = logging.StreamHandler()  # Keep console handler as is

logger.addHandler(file_handler)
logger.addHandler(console_handler)
