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
    
    def mark_as_seen(self, chat_id, message_id):
        url = f"{self.__api_url}/api/sendSeen"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "chatId": chat_id,
            "messageIds": [message_id],
            "participant": None,
            "session": self.__instance_key
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code not in [200, 201]:
                logger.error(f"[WAHA][mark_as_seen] Falha ao marcar como lida: {response.status_code} | {response.text}")
        except Exception as e:
            logger.error(f"[WAHA][mark_as_seen] Exceção ao marcar como lida: {e}")
