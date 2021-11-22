FROM python:3.8-slim

COPY . /code

WORKDIR /code

RUN pip install --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/* \
    && rm -rf /var/lib/apt/lists/*

CMD python -u main.py