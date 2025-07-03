from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import GOOGLE_CALENDAR_ID, GOOGLE_CREDENTIALS_PATH  # <-- do seu config.py

SCOPES = ['https://www.googleapis.com/auth/calendar']

calendar_id = GOOGLE_CALENDAR_ID

credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_PATH,
    scopes=SCOPES
)

service = build('calendar', 'v3', credentials=credentials)


class ServicesCalendar:

    @staticmethod
    def criar_servico_calendar():
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH,  
            scopes=SCOPES
        )
        service = build('calendar', 'v3', credentials=credentials)
        return service
    
    @staticmethod
    def criar_evento(nome_paciente, data_inicio, data_fim):
        event = {
            'summary': f'Consulta de Quiropraxia - {nome_paciente}',
            'start': {
                'dateTime': data_inicio,
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': data_fim,
                'timeZone': 'America/Sao_Paulo',
            },
        }
        return event

    @staticmethod
    def inserir_evento(service, event):
        created_event = service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID,  # seu email de agenda
            body=event
        ).execute()
        return created_event

    @staticmethod
    def buscar_eventos_do_dia(service, data: str):
        try:
            time_min = f"{data}T07:00:00-03:00"
            time_max = f"{data}T20:00:00-03:00" 

            eventos = service.events().list(
                calendarId=GOOGLE_CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return eventos.get('items', [])
        
        except Exception as e:
            print("Erro ao buscar eventos:", e)
            return []