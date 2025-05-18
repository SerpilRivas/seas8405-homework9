# -------- STAGE 1: Build dependencies --------
FROM python:3.13-alpine AS builder

WORKDIR /app

# Install system tools for build (like netcat if needed)
RUN apk add --no-cache netcat-openbsd

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

COPY . .

# -------- STAGE 2: Runtime container --------
FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN adduser -D appuser

WORKDIR /app

# Copy just the installed packages and code from builder
COPY --from=builder /install /usr/local
COPY --from=builder /app .

USER appuser

# Add a HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD nc -z localhost 5000 || exit 1

CMD ["python", "app.py"]


