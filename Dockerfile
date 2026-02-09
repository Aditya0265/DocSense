# Base Image: Lightweight Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Required for CV2/GL and Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "EXP_PDF-Extractor/app.py", "--server.port=8501", "--server.address=0.0.0.0"]