FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci --only=production && \
    npm install @vercel/analytics @vercel/web-vitals

COPY frontend/ ./

RUN npm run build || true

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
