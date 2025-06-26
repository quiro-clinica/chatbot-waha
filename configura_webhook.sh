#!/bin/sh

WAHA_URL="http://waha:3000"
WEBHOOK_URL="http://bot:8000/webhook"
SESSION_NAME="default"

echo "⌛ Aguardando Waha iniciar..."

# Espera Waha responder com status HTTP 200
until curl -s -o /dev/null -w "%{http_code}" "${WAHA_URL}/api/server/status" | grep -q "200"; do
  echo "Waha ainda não respondeu... tentando novamente..."
  sleep 5
done

# Envia o webhook
curl -s -X PUT "${WAHA_URL}/api/sessions/${SESSION_NAME}" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "webhooks": [
        {
          "url": "'"${WEBHOOK_URL}"'",
          "events": ["message"]
        }
      ]
    }
  }'

echo "✅ Webhook configurado com sucesso para sessão '${SESSION_NAME}'!"
