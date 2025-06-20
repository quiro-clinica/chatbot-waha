from redis_tools.redis_queue import dequeue, get_first_in_queue, remove_from_set
from redis_tools.redis_pending_messages import get_pending_message, delete_pending_message
from core.ai_bot import AIBot
from services.evolution_api import send_whatsapp_message

bot = AIBot()

def finalizar_atendimento(chat_id: str):
    print(f"[ATENDIMENTO] Finalizando atendimento para {chat_id}...")
    
    chat_removido = dequeue()
    if chat_removido:
        remove_from_set(chat_removido)


    proximo = get_first_in_queue()

    if proximo:
        print(f"[ATENDIMENTO] Próximo da fila é {proximo}. Verificando mensagem pendente...")

        mensagem_pendente = get_pending_message(proximo)

        if mensagem_pendente:
            print(f"[ATENDIMENTO] Mensagem pendente encontrada. Invocando IA...")
            delete_pending_message(proximo)  # Limpa depois de usar
            resposta = bot.invoke(mensagem_pendente, chat_id=proximo)

            send_whatsapp_message(
                number=proximo,
                text=resposta
            )
        
    else:
        print("[ATENDIMENTO] Fila vazia.")
