FROM python:3.6

ENV SHELL /bin/bash

COPY . /web
WORKDIR /web

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    chmod +x classify *.sh *.py

CMD ./run.sh