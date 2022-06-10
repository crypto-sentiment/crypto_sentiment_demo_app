FROM python:3.9-slim

WORKDIR /root

COPY requirements.txt /root
RUN python3 -m pip install --upgrade pip

# the Spacy part is copied from ibbd/spacy
RUN pip3 install -r requirements.txt && python3 -m spacy download en \
    && python3 -m spacy download xx

ENV PYTHONPATH "${PYTHONPATH}:/root/crypto_sentiment_demo_app"
ENV PYTHONPYCACHEPREFIX=/tmp/cpython/

COPY . /root
