# Use a lightweight Python 3.10 image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Default command when container runs
CMD ["bash"]

