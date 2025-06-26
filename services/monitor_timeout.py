import time
from datetime import datetime

from redis import Redis
from redis_tools.redis_timeout import obter_timestamp, remover_timestamp
from services.atendimento import finalizar_atendimento

# Conectando ao Redis DB10 onde os timestamps são salvos
redis_timeout = Redis(host="redis", port=6379, db=10, decode_responses=True)

TIMEOUT = 300  # 5 minutos

def monitorar_timeout():
    print("[MONITOR TIMEOUT] Iniciado...")

    while True:
        time.sleep(30)

        # Busca todos os usuários que têm um timestamp salvo
        chaves = redis_timeout.keys("ultimo_uso:*")

        for chave in chaves:
            chat_id = chave.replace("ultimo_uso:", "")
            timestamp = obter_timestamp(chat_id)

            if not timestamp:
                continue

            agora = datetime.utcnow().timestamp()
            inatividade = agora - timestamp

            if inatividade > TIMEOUT:
                print(f"[TIMEOUT] {chat_id} inativo por {int(inatividade)} segundos. Finalizando atendimento.")
                finalizar_atendimento(chat_id)
                
