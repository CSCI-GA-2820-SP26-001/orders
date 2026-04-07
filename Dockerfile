FROM python:3.12-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

COPY service/ ./service/
COPY wsgi.py .

ENV PORT=8080
EXPOSE 8080

CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "wsgi:app"]
