FROM python:3.9-slim

COPY . /root
WORKDIR /root

RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/root/crypto_sentiment_demo_app"