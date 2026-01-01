# Use a slim Python 3.11 base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install uv, the project's package manager
RUN pip install uv

# Copy all files first
COPY . .

# Install ingestion (ETL) dependencies
RUN uv pip install --system --no-cache .[etl]
