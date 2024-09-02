FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy the Django settings file from the docker_config folder
COPY docker_config/settings.py /app/enterpriseApi/settings.py

COPY . /app
