from core.ai_bot import AIBot
from services.waha_api import Waha
from logger_config import logger

from redis_tools.redis_queue import dequeue, get_first_in_queue, remove_from_set
from redis_tools.redis_pending_messages import get_pending_message, delete_pending_message
from redis_tools.redis_timeout import remover_timestamp, salvar_timestamp

waha = Waha()

bot = AIBot()

def finalizar_atendimento(chat_id: str):
    try:
        logger.info(f"[ATENDIMENTO] Finalizando atendimento para {chat_id}...")

        remover_timestamp(chat_id)
        chat_removido = dequeue()
        if chat_removido:
            remove_from_set(chat_removido)

        proximo = get_first_in_queue()

        if proximo:
            logger.info(f"[ATENDIMENTO] Próximo da fila é {proximo}. Verificando mensagem pendente...")

            mensagem_pendente = get_pending_message(proximo)
            if mensagem_pendente:
                logger.info(f"[ATENDIMENTO] Mensagem pendente encontrada. Invocando IA...")
                resposta = bot.invoke(mensagem_pendente, chat_id=proximo)
                waha.send_whatsapp_message(chat_id=proximo, message=resposta)
                salvar_timestamp(proximo)
                delete_pending_message(proximo)
        else:
            logger.info("[ATENDIMENTO] Fila vazia.")

    except Exception as e:
        logger.error(f"[ERRO][ATENDIMENTO] Falha ao finalizar atendimento: {e}")