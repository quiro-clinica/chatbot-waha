from fastapi import APIRouter, Request
from services.evolution_api import send_whatsapp_message
from core.ai_bot import AIBot

bot = AIBot()
router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    chat_id = data.get('data').get('key').get('remoteJid')
    message = data.get('data').get('message').get('conversation')

    if chat_id and message and not '@g.us' in chat_id:
        resposta_ia = bot.invoke(message)

        send_whatsapp_message(
            number=chat_id,
            text=resposta_ia
        )

    return {'status': 'ok'}