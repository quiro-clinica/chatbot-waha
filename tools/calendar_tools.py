import json

from typing import List
from datetime import datetime
from pydantic import BaseModel

from langchain_core.tools import tool
from langchain.tools.base import ToolException

from services.services_calendar import ServicesCalendar
from validadores import validar_dia
from logger_config import logger

service = ServicesCalendar.criar_servico_calendar()

class MarcarConsultaInput(BaseModel):
    nome_paciente: str
    data_inicio: str
    data_fim: str  

def marcar_consulta(nome_paciente: str, data_inicio: str, data_fim: str) -> str:
    event = ServicesCalendar.criar_evento(nome_paciente, data_inicio, data_fim)
    created_event = ServicesCalendar.inserir_evento(service, event)
    return f"Consulta marcada com sucesso: {created_event.get('htmlLink')}"

@tool
def marcar_consulta_wrapper(input_data: str) -> str:
    """
    Recebe uma string JSON com nome_paciente, data_inicio e data_fim. Depois marca a consulta no Google Calendar.
    """
    try:
        input_dict = json.loads(input_data)
        return marcar_consulta(
            nome_paciente=input_dict["nome_paciente"],
            data_inicio=input_dict["data_inicio"],
            data_fim=input_dict["data_fim"]
        )
    except Exception as e:
        logger.error(f"[ERRO] Falha ao marcar consulta com dados: {input_data} | Erro: {e}")
        return f"Erro ao processar os dados da consulta: {str(e)}"



def gerar_horarios_disponiveis() -> List[str]:
    """Gera a lista de horários possíveis entre 07:00–12:00 e 13:00–19:00."""
    horarios = [f"{h:02d}:00" for h in range(7, 12)] 
    horarios += [f"{h:02d}:00" for h in range(13, 19)]  
    return horarios


consulta_concluida = False #da tool abaixo

@tool
def ver_horarios_disponiveis(data: str) -> str:
    """
    Retorna os horários disponíveis para uma data específica no formato 'YYYY-MM-DD'.
    """
    try:
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            raise ToolException(f"Formato inválido para a data: '{data}'. Use 'YYYY-MM-DD'.")

        data_formatada = data_obj.strftime("%d-%m-%Y")
        mensagem_erro = validar_dia(data_formatada)

        if mensagem_erro:
            raise ToolException(mensagem_erro)

        horarios = gerar_horarios_disponiveis()
        eventos = ServicesCalendar.buscar_eventos_do_dia(service, data)

        ocupados = [evento['start']['dateTime'][11:16] for evento in eventos]
        livres = [h for h in horarios if h not in ocupados]

        if not livres:
            return f"Não há horários disponíveis para {data}."

        return f"Horários disponíveis para {data}: {', '.join(livres)}."

    except ToolException as e:
        from logger_config import logger
        logger.warning(f"[ToolException] ver_horarios_disponiveis: {e} | data='{data}'")
        raise e

    except Exception as e:
        from logger_config import logger
        logger.error(f"[ERRO] ver_horarios_disponiveis falhou: {e} | data='{data}'")
        raise ToolException(f"Erro ao verificar horários disponíveis: {str(e)}")
