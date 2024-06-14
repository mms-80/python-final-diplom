FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt
WORKDIR /app
COPY . /app