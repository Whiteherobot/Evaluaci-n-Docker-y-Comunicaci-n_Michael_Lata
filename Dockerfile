FROM python:3.9-slim

WORKDIR /app

RUN pip install websockets

COPY The_Initiator.py .
COPY The_Transformer.py .
COPY The_Auditor.py .
