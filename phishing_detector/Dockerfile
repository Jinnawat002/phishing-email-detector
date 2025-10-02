# Base image
FROM python:3.12.4-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy requirements and the new build script
COPY requirements.txt .
COPY build.sh .
RUN chmod +x ./build.sh # ทำให้ script ทำงานได้

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Run gunicorn (Start command)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "phishing_detector.wsgi:application"]