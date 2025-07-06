import asyncio
from datetime import datetime, timezone

from redis import Redis
from redis_tools.redis_timeout import obter_timestamp

from services.atendimento import finalizar_atendimento_abandonado
from logger_config import logger
from services.waha_api import Waha

waha = Waha()

redis_timeout = Redis(host="redis", port=6379, db=10, decode_responses=True)

TIMEOUT = 1500  # 2 minutos

async def monitorar_timeout():
    while True:
        await asyncio.sleep(30)

        try:
            chaves = redis_timeout.keys("ultimo_uso:*")

            for chave in chaves:
                chat_id = chave.replace("ultimo_uso:", "")
                timestamp = obter_timestamp(chat_id)

                if not timestamp:
                    continue

                agora = datetime.now(timezone.utc).timestamp()
                inatividade = agora - timestamp

                if inatividade > TIMEOUT:
                    logger.info(f"[TIMEOUT] {chat_id} inativo por {int(inatividade)} segundos. Finalizando atendimento.")
                    finalizar_atendimento_abandonado(chat_id)
                    try:
                        waha.send_whatsapp_message(chat_id, "Encerramos o atendimento por inatividade. Se precisar de algo, é só mandar uma nova mensagem. 😊")
                        logger.info(f"[TIMEOUT] Mensagem de encerramento enviada para {chat_id}.")
                    except Exception as e:
                        logger.error(f"[TIMEOUT][ERRO] Falha ao enviar mensagem de encerramento: {e}")

        except Exception as e:
            logger.error(f"[ERRO][TIMEOUT] Falha ao monitorar/finalizar atendimento: {e}")
