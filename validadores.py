from datetime import datetime

# Dias válidos (segunda a sábado)
DIAS_VALIDOS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def eh_dia_valido(data_str: str) -> bool:
    
    try:
        data = datetime.strptime(data_str, "%d-%m-%Y")
        dia_semana = data.strftime("%A")  # Retorna: Monday, Tuesday...
        return dia_semana in DIAS_VALIDOS
    except ValueError:
        return False  # Data inválida
    
def eh_data_no_futuro(data_str: str) -> bool:
    
    try:
        data_desejada = datetime.strptime(data_str, "%d-%m-%Y").date()
        hoje = datetime.now().date()
        return data_desejada >= hoje
    except ValueError:
        return False  # Data inválida
    
def validar_dia(data_str: str):
    """
    Valida se a data está em um dia útil e se ainda está no futuro.
    :param data_str: string no formato "DD-MM-YYYY"
    :return: Mensagem de erro ou None se estiver tudo certo
    """
    if not eh_dia_valido(data_str):
        return "Desculpe, não atendemos nesse dia da semana. Escolha um dia de segunda a sábado."
    
    if not eh_data_no_futuro(data_str):
        return "Essa data já passou. Por favor, escolha uma data futura."

    return None  # Tudo certo

def mensagem_invalida(chat_id: str, message: str) -> bool:
    return (
        not chat_id
        or not message
        or "@g.us" in chat_id
        or chat_id.startswith("status@broadcast")
        or chat_id.startswith("0@c.us")
    )

    


