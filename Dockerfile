FROM python:3.6

ENV SHELL /bin/bash

COPY . /web
WORKDIR /web

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    chmod +x run.sh && \
    chmod +x classify

CMD ./run.sh