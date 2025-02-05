
# Use an official Python runtime as a parent image.
FROM python:3.10-slim

# Install build dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Upgrade pip and install pipenv.
RUN pip install --upgrade pip && pip install pipenv

# Set the working directory in the container to /app.
WORKDIR /app

# Copy the Pipfile and Pipfile.lock first for dependency caching.
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv (including dev dependencies for hot reload).
RUN pipenv install --dev

# Copy the rest of the application code.
COPY . .

# Expose port 8000.
EXPOSE 8000

# Run the FastAPI application using uvicorn through pipenv.
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

