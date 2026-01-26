import logging
import sys

logger = logging.getLogger('bitcoin')
logger.setLevel(logging.DEBUG)

# Handler do pliku
file_handler = logging.FileHandler('bitcoin.log',
    mode='w',
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)

# Handler do konsoli
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Tylko ważne komunikaty

# Format
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)