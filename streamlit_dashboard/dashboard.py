import os
import sys
import streamlit as st
from sqlalchemy.exc import IntegrityError

# Caminho base do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# Imports internos
from redis_tools.redis_pending_ids import (
    get_all_chat_ids,
    get_chat_id_from_redis,
    delete_chat_id
)
from database import SessionLocal
from models import ChatIdMap  # modelo da tabela chat_id_map

st.set_page_config(page_title="Painel do Chatbot", layout="wide")

st.title("Painel de Controle do Chatbot")

# ============================
# 🔹 Lista de IDs pendentes
# ============================
st.subheader("Lista de IDs pendentes no Redis")
pending_ids = get_all_chat_ids()

if pending_ids:
    for chat_id in pending_ids:
        pushname = get_chat_id_from_redis(chat_id) or "Desconhecido"
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"{chat_id} — {pushname}")
        with col2:
            if st.button("Remover", key=f"del_{chat_id}"):
                delete_chat_id(chat_id)
                st.success(f"Removido: {chat_id}")
                st.experimental_rerun()
else:
    st.info("Nenhum número pendente no Redis.")

# ============================
# 🔹 Associação ID ↔ Número
# ============================
# 🔹 Associação ID ↔ Número
st.subheader("Associar ID ao número real do WhatsApp")

redis_ids = get_all_chat_ids()

if redis_ids:  # <- Garante que o formulário só aparece se houver ID
    with st.form("form_associar"):
        selected_id = st.selectbox("Selecione um ID pendente", redis_ids)
        numero_real_bruto = st.text_input("Digite o número (somente DDD + número)")

        submitted = st.form_submit_button("Salvar associação")
        if submitted:
            if not numero_real_bruto.isdigit() or len(numero_real_bruto) < 10:
                st.warning("Digite apenas números válidos com DDD (ex: 81999999999)")
            else:
                numero_formatado = f"55{numero_real_bruto}@s.whatsapp.net"

                db = SessionLocal()
                try:
                    nova_entrada = ChatIdMap(
                        chat_id_lid=selected_id,
                        chat_id_real=numero_formatado
                    )
                    db.add(nova_entrada)
                    db.commit()
                    delete_chat_id(selected_id)

                    st.success(f"Salvo: {selected_id} → {numero_formatado}")
                    st.rerun()
                except IntegrityError:
                    db.rollback()
                    st.warning("Esse ID ou número já foi salvo.")
                except Exception as e:
                    db.rollback()
                    st.error(f"Erro ao salvar: {e}")
                finally:
                    db.close()
else:
    st.info("Nenhum ID disponível no Redis para associar.")

# ============================
# 🔹 Números já salvos
# ============================
st.subheader("Números já salvos no PostgreSQL")

db = SessionLocal()
try:
    results = db.query(ChatIdMap.chat_id_lid, ChatIdMap.chat_id_real).all()
    if results:
        for chat_id_lid, chat_id_real in results:
            st.write(f"{chat_id_lid} → {chat_id_real}")
    else:
        st.info("Nenhum número foi salvo ainda.")
except Exception as e:
    st.error(f"Erro ao acessar PostgreSQL: {e}")
finally:
    db.close()
