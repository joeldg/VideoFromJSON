FROM python:3.10-slim

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 5000 5001

CMD ["sh", "-c", "python VideoFromJSONAPI/application.py & python VideoFromJSONWeb/application.py & nginx -g 'daemon off;'"]