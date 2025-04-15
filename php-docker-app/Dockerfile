# Sử dụng image PHP với Apache
FROM php:8.2-apache

# Cài đặt các tiện ích cần thiết (nếu cần)
RUN docker-php-ext-install mysqli

# Cấu hình thư mục chứa mã nguồn (gán nó vào thư mục /var/www/html của Apache)
VOLUME ["/var/www/html"]

# Mở cổng 80 cho Apache
EXPOSE 80
