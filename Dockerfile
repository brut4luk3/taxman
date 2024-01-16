# Base image
FROM python:3.8-slim

# Install Tesseract and Portuguese language package
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-por

# Set the TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5.3.0/tessdata/

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Start the application
CMD ["python", "app.py"]