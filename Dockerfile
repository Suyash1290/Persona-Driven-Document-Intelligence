# Dockerfile for Adobe Hackathon Challenge 1b
# Compatible with AMD64 architecture
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY HackathonChallenge/ ./HackathonChallenge/
COPY project1b.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set the entry point to the main processing script
ENTRYPOINT ["python", "project1b.py"] 