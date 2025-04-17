FROM node:16-slim

WORKDIR /app

RUN npm init -y && \
    npm install express redis@3 gelf-pro

COPY . /app/

EXPOSE 80

CMD ["node", "webui.js"]
