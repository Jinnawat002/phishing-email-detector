#!/bin/sh

# หยุดการทำงานทันทีถ้ามีคำสั่งไหนล้มเหลว
set -e

# รัน database migrations
echo "Running database migrations..."
python manage.py migrate

# เริ่มการทำงานของ Gunicorn server
# exec จะทำให้ gunicorn เป็น process หลักของ container
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 phishing_detector.wsgi:application