FROM python:3.11-slim

# Ngăn Python tạo file .pyc và tối ưu log output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Cài đặt gcc và libpq-dev cần thiết để biên dịch driver PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào image
COPY . .

# Mở cổng 5000
EXPOSE 5000

# Lệnh khởi chạy ứng dụng với Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]