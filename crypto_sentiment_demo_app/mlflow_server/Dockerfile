FROM python:3.9-slim

WORKDIR /mlflow
COPY create_bucket.py create_bucket.py
COPY start.sh start.sh

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENV PYTHONPYCACHEPREFIX=/tmp/cpython/
