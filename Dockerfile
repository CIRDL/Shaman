# Latest python image
FROM python:3.13-slim-bookworm

# Working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Poetry
RUN pip install poetry

# Copy only the dependency files first for caching
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the rest of your code
COPY . .

# Default command (can be overridden by docker-compose)
CMD ["poetry", "run", "python", "app/ingest/catalog/bronze_cs.py"]