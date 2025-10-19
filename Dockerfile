FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip/setuptools/wheel before installing deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Install pre-commit explicitly (safety net)
RUN pip install --no-cache-dir pre-commit

COPY . .

# Install hooks (non-fatal if none exist yet)
RUN pre-commit install --install-hooks || true

CMD ["bash"]
