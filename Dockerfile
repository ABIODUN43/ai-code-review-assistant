# Use lightweight Python base image
FROM python:3.10-slim

# Install system build tools (needed for some Python deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install pre-commit explicitly (to be safe)
RUN pip install --no-cache-dir pre-commit

# Copy the rest of the repo
COPY . .

# Ensure pre-commit hooks are installed in container
RUN pre-commit install --install-hooks || true

# Default command
CMD ["bash"]
