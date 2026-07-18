FROM python:3.12-slim

WORKDIR /app

COPY shared/ ./shared/
COPY ata/    ./ata/

COPY sentinel/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY sentinel/ ./

ENV SERVICE_NAME=sentinel

CMD ["python", "sentinel.py"]

