import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CURRATE_RU = os.getenv('CURRATE_RU')
OWM_TOKEN = os.getenv('OWM_TOKEN')

