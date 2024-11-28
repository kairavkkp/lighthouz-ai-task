FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

RUN python -m venv /venv
COPY requirements.txt /code/
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /code/
ENV PATH="/venv/bin:$PATH"
