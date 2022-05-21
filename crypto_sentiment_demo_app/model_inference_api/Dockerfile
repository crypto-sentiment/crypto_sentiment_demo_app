FROM python:3.9-slim

WORKDIR /root

RUN apt update -y && \
    apt upgrade -y && \
    apt install -y curl locales locales-all && \
    rm -rf /var/lib/apt/lists/*

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

COPY requirements.txt /root
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/root/crypto_sentiment_demo_app"

COPY . /root
