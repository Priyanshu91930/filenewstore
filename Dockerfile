# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY . .

CMD ["python", "bot.py"]
