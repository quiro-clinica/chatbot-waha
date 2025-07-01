#!/bin/sh

# Inicia o Uvicorn em segundo plano
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Aguarda um pouco para o bot iniciar (ou use healthcheck)
sleep 20

# Executa o script que configura o webhook
./configura_webhook.sh

# Espera o processo do uvicorn
wait
