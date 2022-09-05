FROM python:3.8.12-slim

WORKDIR /usr/src/aurora

# dont write pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# dont buffer to stdout/stderr
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /usr/src/aurora/frontend/app/requirements.txt

# dependencies
RUN set -eux \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/src/aurora/frontend/app/requirements.txt \
    && rm -rf /root/.cache/pip

COPY ./ /usr/src/aurora