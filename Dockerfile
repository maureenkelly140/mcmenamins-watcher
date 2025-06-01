# Use official Python base with Playwright + system dependencies
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Chromium browser with necessary system dependencies
RUN playwright install --with-deps chromium

# Default command: run your script
CMD ["python", "main.py"]
