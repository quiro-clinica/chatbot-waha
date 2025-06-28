# Chatbot Inteligente para Agendamento com IA (Waha)

> Sistema de atendimento inteligente para WhatsApp com agendamento via Google Calendar, cache com Redis, orquestração via Docker e persistência de sessão via Waha.

---

## Visão Geral

Este projeto é um chatbot com IA que atua como assistente para agendamento de sessões de quiropraxia via WhatsApp, usando a API Waha (substituindo a Evolution API). Ele entende mensagens com IA (LangChain + Groq), faz marcações no Google Calendar, usa Redis e PostgreSQL para cache e persistência, e é orquestrado com Docker.

---

## Tecnologias Utilizadas

| Camada            | Ferramenta                  |
| ----------------- | --------------------------- |
| Backend Principal | **FastAPI**                 |
| LLM               | **LangChain + Groq**        |
| Banco de Dados    | **PostgreSQL**              |
| Cache e Filas     | **Redis (vários DBs)**      |
| Persistência Sessão | **Waha Sessions (pasta local)** |
| Integração Agenda | **Google Calendar API**     |
| Contato WhatsApp  | **Waha API**                |
| Orquestração      | **Docker + Docker Compose** |

---

## Passo Importante: Pasta para Persistência da Sessão Waha

Para que o Waha mantenha a conexão ativa e persistente, **é obrigatório** que o usuário que usar este repositório crie uma pasta local chamada:

```bash
waha_sessions
```

Essa pasta será usada como volume para armazenar as sessões de WhatsApp, evitando perda da sessão após reinícios do container.

## Como Executar o Projeto

1. Clone o repositório e acesse a pasta
```bash
git clone https://github.com/seu-usuario/chatbot-waha.git
cd chatbot-waha
```

2. Crie a pasta de sessões do Waha (se ainda não existir)
```bash
mkdir waha_sessions
```

3. Configure o arquivo .env (exemplo básico)
```bash
# Configurações da sessão Waha
WAHA_API_URL=http://waha:3000
WAHA_INSTANCE_KEY=default
WAHA_WEBHOOK_URL=http://bot:8000/webhook

# Agenda Google Calendar
GOOGLE_CALENDAR_ID=seu_email
GOOGLE_CREDENTIALS_PATH=/app/google-credentials.json

# Configuração opcional de versão do WhatsApp Web
CONFIG_SESSION_PHONE_VERSION=2.3000.1023818200

# PostgreSQL (mantido para uso futuro)
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://postgres:postgres@postgres:5432/waha
DATABASE_CONNECTION_CLIENT_NAME=waha_exchange

# Redis (cache, fila, timeout, etc)
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=redis://redis:6379/6
CACHE_LOCAL_ENABLED=false

# LLM com Groq
GROQ_API_KEY=sua_groq_api_key_aqui


```

4. Adicione o arquivo google-credentials.json na raiz do projeto (obtido no Google Cloud Console).

5. Suba os containers com Docker
```bash
docker-compose up --build -d
```

## Status Atual do Projeto
✔ Integração com Waha funcionando
✔ Persistência de sessão configurada
✔ Webhook automático
✔ IA conectada com Groq
✔ Agendamento via Google Calendar
✔ Redis pronto para cache e controle de estado
✔ PostgreSQL habilitado para uso futuro

## Requisitos Externos
| Serviço             | Finalidade                      | Como configurar                                      |
| ------------------- | ------------------------------- | ---------------------------------------------------- |
| **Groq API**        | Processamento de linguagem      | [https://console.groq.com]
| **Google Calendar** | Marcação automática de horários | Google Cloud Console + `google-credentials.json`     |
| **Waha**            | Integração com WhatsApp via API | Suba localmente com Docker e escaneie o QR Code      |


