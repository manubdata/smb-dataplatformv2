# Use a slim Python 3.11 base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install uv, the project's package manager
RUN pip install uv

# Copy all files first
COPY . .

# Install transformation (dbt) dependencies
RUN uv pip install --system --no-cache .[dbt]

# Install dbt packages
RUN uv run poe dbt-deps

# Set the command to run the dbt build for production
CMD ["uv", "run", "poe", "dbt-build-prod"]
