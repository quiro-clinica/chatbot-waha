import requests

from config import WAHA_API_URL, WAHA_INSTANCE_KEY
from logger_config import logger

class Waha:

    def __init__(self):
        self.__api_url = WAHA_API_URL
        self.__instance_key = WAHA_INSTANCE_KEY

    def send_whatsapp_message(self, chat_id, message):
        url = f'{self.__api_url}/api/sendText'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'session': self.__instance_key,
            'chatId': chat_id,
            'text': message,
        }
        requests.post(
            url=url,
            json=payload,
            headers=headers,
        )


