FROM python:3.6

ENV SHELL /bin/bash

COPY . /web
WORKDIR /web

RUN pip install --upgrade pip && \
    pip install -r requirements.txt 

CMD ./classify get_models && \
    ./classify classify && \
    ./classify entities && \
    ./classify listbuilding_fundraising_classify