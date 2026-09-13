FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# WeasyPrint native libraries + Arabic/Latin fonts (standard Debian paths,
# registered in the ldconfig cache so ctypes.util.find_library works).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    libharfbuzz0b \
    libfribidi0 \
    libfontconfig1 \
    fonts-noto-core \
    fonts-dejavu-core \
    shared-mime-info \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static at build time (fails the build safely if misconfigured,
# leaving the previous deploy running).
RUN python manage.py collectstatic --noinput

# Run migrations then start the server, binding to Railway's $PORT.
CMD python manage.py migrate --noinput && \
    gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
