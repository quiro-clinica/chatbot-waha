import os

from dotenv import load_dotenv


load_dotenv()

WAHA_API_URL = os.getenv('WAHA_API_URL')
WAHA_INSTANCE_KEY = os.getenv('WAHA_INSTANCE_KEY')

DATABASE_URL = os.getenv("DATABASE_CONNECTION_URI").replace("'", "")

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")