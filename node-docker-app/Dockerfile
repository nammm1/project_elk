# Sử dụng Node.js 18 làm base image
FROM node:18

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép package.json và package-lock.json vào container
COPY package*.json ./

# Cài đặt dependencies
RUN npm install

# Sao chép toàn bộ source code vào container
COPY . .

# Expose cổng 3000 để truy cập ứng dụng
EXPOSE 3000

# Chạy ứng dụng Node.js
CMD ["node", "server.js"]
