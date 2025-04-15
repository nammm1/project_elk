# Sử dụng PostgreSQL 15 làm base image
FROM postgres:15

# Thiết lập biến môi trường mặc định (có thể override khi chạy container)
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword
ENV POSTGRES_DB=mydatabase

# Sao chép file SQL vào thư mục tự động thực thi của PostgreSQL
COPY init-db.sql /docker-entrypoint-initdb.d/

# Mở cổng 5432
EXPOSE 5432
