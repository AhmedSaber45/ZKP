FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH=/app

#tell flask which file contain your application instance 
ENV FLASK_APP=app.py


WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libpq-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
# Ensure gunicorn is installed for serving the app
RUN pip install gunicorn

COPY . .



EXPOSE 5000
CMD ["gunicorn", "--chdir", "/app", "--pythonpath", "/app", "--bind", "0.0.0.0:5000", "--log-level", "debug", "app:app"]