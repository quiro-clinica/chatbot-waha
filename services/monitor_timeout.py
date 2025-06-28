import asyncio
from datetime import datetime
from redis import Redis
from redis_tools.redis_timeout import obter_timestamp
from services.atendimento import finalizar_atendimento
from logger_config import logger

redis_timeout = Redis(host="redis", port=6379, db=10, decode_responses=True)

TIMEOUT = 1500  # 25 minutos

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

                agora = datetime.utcnow().timestamp()
                inatividade = agora - timestamp

                if inatividade > TIMEOUT:
                    logger.info(f"[TIMEOUT] {chat_id} inativo por {int(inatividade)} segundos. Finalizando atendimento.")
                    finalizar_atendimento(chat_id)

        except Exception as e:
            logger.error(f"[ERRO][TIMEOUT] Falha ao monitorar/finalizar atendimento: {e}")
