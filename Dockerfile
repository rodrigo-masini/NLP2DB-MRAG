FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download zh_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs pilot/data pilot/message_history

# Expose port
EXPOSE 7860

# Run the application
CMD ["python", "run.py"]
