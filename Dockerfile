FROM python:3.6

ENV SHELL /bin/bash
RUN pip install pipenv
RUN apt-get update && apt-get install -y wget
COPY . /web
WORKDIR /web

CMD  pipenv install && \
    pipenv run ./classify get_models && \
    pipenv run ./classify classify && \
    pipenv run ./classify entities && \
    pipenv run ./classify listbuilding_fundraising_classify
