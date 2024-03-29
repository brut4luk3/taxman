# Base image
FROM python:3.8-slim

# Install Tesseract
RUN apt-get update && \
    apt-get install -y tesseract-ocr wget

# Manually download Portuguese training data
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata -P /usr/share/tesseract-ocr/tessdata/

# Set the TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata/

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Start the application
CMD ["python", "app.py"]