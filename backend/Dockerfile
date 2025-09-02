FROM python:3.11-slim-bullseye

RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list \
 && sed -i 's|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]