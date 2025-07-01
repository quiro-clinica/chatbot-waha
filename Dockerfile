FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev postgresql-dev curl

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY google-credentials.json /app/google-credentials.json

# Copia o novo entrypoint
COPY entrypoint.sh /app/entrypoint.sh

# Dá permissão
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Usa forma recomendada (lista JSON)
ENTRYPOINT ["/app/entrypoint.sh"]

