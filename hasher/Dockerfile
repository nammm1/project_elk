FROM python:3.12-alpine

# Cài các dependency cần thiết để build và chạy Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

# Cài đặt các thư viện Python cần thiết
RUN pip install --no-cache-dir Flask pygelf

# Tạo thư mục làm việc
WORKDIR /app

# Copy mã nguồn vào container
COPY hasher.py .

# Mở port 80 (có thể tùy chỉnh nếu bạn dùng cổng khác trong Flask)
EXPOSE 80

# Chạy ứng dụng
CMD ["python", "hasher.py"]
