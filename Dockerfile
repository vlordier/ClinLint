# Use an optimized base image for Python 3.11
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Copy dependency files first to leverage caching
COPY requirements/base.txt ./requirements/

# Install production dependencies
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy application code
COPY src app

# Expose port for FastAPI
EXPOSE 80

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
