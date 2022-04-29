FROM python:3.8-slim

COPY . /root
WORKDIR /root

RUN python -m pip install --upgrade pip
#RUN pip3 install --quiet --no-cache-dir poetry
#ADD pyproject.toml .
#ADD poetry.lock .
#RUN poetry install
ADD requirements.txt .
RUN pip3 install -r requirements.txt