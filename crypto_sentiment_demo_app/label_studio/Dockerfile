FROM heartexlabs/label-studio:latest

WORKDIR /label-studio

COPY requirements.txt /label-studio
#RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/home/crypto_sentiment_demo_app"
ENV PYTHONPATH "${PYTHONPATH}:/label-studio/.local/bin"
ENV PYTHONPYCACHEPREFIX=/tmp/cpython/

COPY . /label-studio/
