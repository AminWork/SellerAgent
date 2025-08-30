FROM python:3.11-slim

WORKDIR /app

# Environment settings to improve reliability in CI/containers
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DEFAULT_TIMEOUT=100

# Copy requirements and install Python dependencies
# Optional: use a custom PyPI mirror by passing build-arg PIP_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements.txt .
RUN if [ -n "$PIP_INDEX_URL" ]; then pip config set global.index-url "$PIP_INDEX_URL" || true; fi \
    && pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
