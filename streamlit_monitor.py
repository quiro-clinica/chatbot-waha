import streamlit as st
import redis
import json
import os
import datetime
from dateutil import parser
from streamlit_autorefresh import st_autorefresh
from streamlit.components.v1 import html
from services.services_calendar import ServicesCalendar

# === CONFIG ===
st.set_page_config(page_title="Painel Bot IA", layout="wide")
st_autorefresh(interval=3000, key="auto_refresh")
LOG_FILE = "logs/app.log"

# === REDIS ===
redis_queue = redis.Redis(host="redis", port=6379, db=7, decode_responses=True)
redis_pending_messages = redis.Redis(host="redis", port=6379, db=8, decode_responses=True)
redis_timeout = redis.Redis(host="redis", port=6379, db=10, decode_responses=True)
redis_client_history = redis.Redis.from_url("redis://redis:6379/5", decode_responses=True)
redis_consultas = redis.Redis(host="redis", port=6379, db=11, decode_responses=True)

# === CALENDAR SERVICE ===
service = ServicesCalendar.criar_servico_calendar()

# === FUNÇÕES ===
def get_fila():
    try:
        return redis_queue.lrange("chatbot_queue", 0, -1)
    except Exception as e:
        return [f"Erro Redis: {e}"]

def ler_logs(n=150):
    if not os.path.exists(LOG_FILE):
        return ["Arquivo de log não encontrado."]
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.readlines()[-n:]

def limpar_logs():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

def resetar_redis():
    redis_pending_messages.flushdb()
    redis_timeout.flushdb()
    redis_queue.flushdb()
    redis_client_history.flushdb()

def get_consultas_marcadas():
    try:
        consultas = redis_consultas.lrange("consultas_marcadas", 0, -1)
        return [json.loads(c) for c in consultas]
    except Exception as e:
        return [{"erro": str(e)}]

def limpar_consultas():
    redis_consultas.delete("consultas_marcadas")

st.markdown("""
    <h1 style='text-align: center; color: #f7f7f7; font-size: 36px; margin-left: 26px;'>
        Gerenciador de Atendimento
    </h1>
""", unsafe_allow_html=True)

# === INTERFACE PRINCIPAL ===
st.markdown("""
    <style>
    /* Fundo geral do app */
    .stApp {
        background-color: #1e1e1e !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Remove a barra superior padrão */
    header {visibility: hidden;}
    /* Remove o rodapé “Made with Streamlit” */
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
# LAYOUT GERAL
col_fila, col_log = st.columns([1, 4])

with col_fila:
    st.subheader("Fila de Espera")
    fila = get_fila()
    if fila:
        for idx, chat_id in enumerate(fila, 1):
            st.code(f"{idx}. {chat_id}")
    else:
        st.info("Fila vazia ou não encontrada.")

with col_log:
    logs = ler_logs()
    log_text = "".join(logs).replace("<", "&lt;").replace(">", "&gt;")
    html(f"""
        <div style='height: 430px; overflow-y: scroll;
                    background: #111; color: #eee;
                    padding: 12px; font-size: 13px;
                    font-family: monospace;
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);'>
            <pre style="white-space: pre-wrap;">{log_text}</pre>
        </div>
        <script>
            const logBox = window.document.querySelector('div[style*="overflow-y: scroll"]');
            logBox.scrollTop = logBox.scrollHeight;
        </script>
    """, height=450)


# Botões centralizados com estilo escuro
col_btn1, col_btn2, col_btn3 = st.columns([2.6, 2, 2.5])
with col_btn2:
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("Limpar Fluxo"):
            limpar_logs()
            st.rerun()
    with btn2:
        if st.button("🚨 Resetar Dados 🚨"):
            resetar_redis()
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)


# TABELAS ALINHADAS
_, col_consultas, col_eventos, _ = st.columns([1, 2, 2, 1])

def formatar_data(data_iso):
    try:
        return datetime.datetime.fromisoformat(data_iso).strftime("%d-%m-%Y %H:%M")
    except:
        return ""

def formatar_hora_fim(data_iso):
    try:
        return datetime.datetime.fromisoformat(data_iso).strftime("%H:%M")
    except:
        return ""

with col_consultas:
    st.subheader("Consultas marcadas hoje:")
    consultas = get_consultas_marcadas()
    dados = []
    for consulta in consultas:
        nome = consulta.get("nome_paciente", "Sem nome")
        inicio = formatar_data(consulta.get("data_inicio", ""))
        fim = formatar_hora_fim(consulta.get("data_fim", ""))
        dados.append({"Nome": nome, "Início": inicio, "Fim": fim})
    while len(dados) < 11:
        dados.append({"Nome": "", "Início": "", "Fim": ""})
    st.dataframe(dados, use_container_width=True, hide_index=True, height=440)
    if st.button("Limpar Consultas Marcadas"):
        limpar_consultas()
        st.success("Consultas limpas com sucesso!")
        st.rerun()

with col_eventos:
    st.subheader("Eventos do Google Calendar hoje:")
    hoje = datetime.date.today().isoformat()
    eventos = ServicesCalendar.buscar_eventos_do_dia(service, hoje)

    dados_eventos = []
    for evento in eventos:
        nome = evento.get("summary", "Sem título")
        hora_inicio_raw = evento['start'].get('dateTime') or evento['start'].get('date')
        try:
            hora_inicio = parser.parse(hora_inicio_raw).strftime("%H:%M")
        except:
            hora_inicio = ""
        dados_eventos.append({"Nome": nome, "Início": hora_inicio})
    while len(dados_eventos) < 11:
        dados_eventos.append({"Nome": "", "Início": ""})
    st.dataframe(dados_eventos, use_container_width=True, hide_index=True, height=440)

st.markdown("<hr>", unsafe_allow_html=True)