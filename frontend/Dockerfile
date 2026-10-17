FROM node:20-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps --prefer-offline

COPY . .

ARG API_PROXY_TARGET=http://api-cognitiva:8000
ENV API_PROXY_TARGET=$API_PROXY_TARGET NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production PORT=8501

RUN npm run build

EXPOSE 8501
CMD ["npm", "start"]
