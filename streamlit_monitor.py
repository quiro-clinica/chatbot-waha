import streamlit as st
import redis
import json
import os
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
from services.services_calendar import ServicesCalendar

st.set_page_config(page_title="Painel Bot IA", layout="wide")

LOG_FILE = "logs/app.log"

st_autorefresh(interval=3000, key="auto_refresh")

# Conexões Redis conforme seu setup
redis_pending_messages = redis.Redis(host="redis", port=6379, db=8, decode_responses=True)
redis_timeout = redis.Redis(host="redis", port=6379, db=10, decode_responses=True)
redis_queue = redis.Redis(host="redis", port=6379, db=7, decode_responses=True)
redis_client_history = redis.Redis.from_url("redis://redis:6379/5", decode_responses=True)
redis_consultas = redis.Redis(host="redis", port=6379, db=11, decode_responses=True)

service = ServicesCalendar.criar_servico_calendar()

def get_fila():
    try:
        return redis_queue.lrange("chatbot_queue", 0, -1)
    except Exception as e:
        return [f"Erro ao acessar Redis: {str(e)}"]

def ler_logs(n=150):
    if not os.path.exists(LOG_FILE):
        return ["Arquivo de log não encontrado."]
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.readlines()[-n:]

def limpar_logs():
    # Escreve vazio no arquivo para limpar
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

def resetar_redis():
    # Apaga todas as chaves dos DBs que você listou
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

# === INTERFACE ===

st.markdown("<h1 style='text-align: center;'>Painel de Monitoramento do Bot</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("📥 Fila de Espera")
    fila = get_fila()
    if fila:
        for idx, chat_id in enumerate(fila, 1):
            st.markdown(f"**{idx}.** `{chat_id}`")
    else:
        st.info("Fila vazia ou não encontrada.")

st.markdown("<h3 style='text-align: center;'>Fluxo em Tempo Real</h3>", unsafe_allow_html=True)

logs = ler_logs()
log_text = "".join(logs).replace("<", "&lt;").replace(">", "&gt;")

components.html(f"""
    <div style="display: flex; justify-content: center;">
        <div style='
            height: 420px;
            width: 100%;
            max-width: 1000px;
            overflow-y: scroll;
            background-color: #111;
            color: #eee;
            padding: 12px;
            font-size: 13px;
            font-family: monospace;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        ' id='log-box'>
            <pre style="white-space: pre-wrap;">{log_text}</pre>
        </div>
    </div>

    <script>
        const logBox = document.getElementById("log-box");
        logBox.scrollTop = logBox.scrollHeight;
    </script>
""", height=440)

col_left, col1, col2, col_right = st.columns([3, 1, 1, 3])

with col1:
    if st.button("Limpar Fluxo", key="btn_limpar_logs"):
        limpar_logs()
        st.success("Logs limpos com sucesso!")
        st.rerun()

with col2:
    if st.button("Resetar Dados", key="btn_resetar_dados"):
        resetar_redis()
        st.success("Todos os Redis foram resetados com sucesso!")
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Consultas Marcadas e Eventos do Dia</h2>", unsafe_allow_html=True)

col_consultas, col_eventos = st.columns(2)

with col_consultas:
    st.subheader("Consultas Marcadas Pelo Bot Hoje")
    consultas = get_consultas_marcadas()
    if consultas:
        for i, consulta in enumerate(consultas, 1):
            nome = consulta.get("nome_paciente", "Sem nome")
            inicio = consulta.get("data_inicio", "")
            fim = consulta.get("data_fim", "")
            link = consulta.get("link_evento", "")
            st.markdown(f"**{i}. {nome}**")
            st.markdown(f" - Início: {inicio}")
            st.markdown(f" - Fim: {fim}")
            st.markdown(f" - [Link do evento]({link})")
    else:
        st.info("Nenhuma consulta marcada.")

    if st.button("Limpar Consultas Marcadas", key="btn_limpar_consultas"):
        limpar_consultas()
        st.success("Consultas marcadas limpas com sucesso!")
        st.rerun()

with col_eventos:
    st.subheader("Eventos no Google Calendar Hoje")
    import datetime
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    eventos = ServicesCalendar.buscar_eventos_do_dia(service, hoje)
    if eventos:
        for i, evento in enumerate(eventos, 1):
            nome = evento.get('summary', 'Sem título')
            inicio = evento['start'].get('dateTime', evento['start'].get('date', ''))
            fim = evento['end'].get('dateTime', evento['end'].get('date', ''))
            st.markdown(f"**{i}. {nome}**")
            st.markdown(f"   - Início: {inicio}")
            st.markdown(f"   - Fim: {fim}")
    else:
        st.info("Nenhum evento agendado para hoje.")

