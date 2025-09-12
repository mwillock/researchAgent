############################
# Base image (common bits) #
############################
FROM python:3.11-slim AS base

#Keep Python lean and logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

#Minmal system deps; add dev if needed later 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

################################
# Builder (cache wheels layer) #
################################
FROM base as builder 

# Install Python deps into wheels
COPY api/requirements.txt /tmp/requirements.txt
RUN pip wheel --wheel-dir /wheels -r /tmp/requirements.txt

#############################
# Runtime (small, non-root) #
#############################
FROM base AS runtime 

#Add a non-root user for better security
RUN adduser --disabled-login --gecos "" appuser
USER appuser

WORKDIR /app

#Install deps from prebuilt wheels (no internet needed here)
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*

#Copy only the API Source 
# (Your build context is repo root, so "api" exists in context)
COPY --chown=appuser:appuser api /app/api

# Default env; Compose will override via env_file
ENV APP_ENV=dev

# Expose FastAPI port
EXPOSE 8000

# Simple healthcheck (optional; Kubernetes/compose can also probe /health)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import socket,sys;s=socket.socket();s.settimeout(2);s.connect(('127.0.0.1',8000));s.close()" || exit 1

# Prod default; dev will override this in compose.dev.yml with --reload + volume mount
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]