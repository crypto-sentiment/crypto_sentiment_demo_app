FROM heartexlabs/label-studio:latest

RUN mkdir -p /home/crypto_sentiment_demo_app

COPY requirements.txt /home/crypto_sentiment_demo_app
RUN pip3 install -r /home/crypto_sentiment_demo_app/requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/home/crypto_sentiment_demo_app"
ENV PYTHONPYCACHEPREFIX=/tmp/cpython/
