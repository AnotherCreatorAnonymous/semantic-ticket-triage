FROM node:20
WORKDIR /app

COPY package.json ./
RUN npm install --legacy-peer-deps --omit=dev

COPY . .

ARG API_PROXY_TARGET=http://api-cognitiva:8000
ENV API_PROXY_TARGET=$API_PROXY_TARGET NEXT_TELEMETRY_DISABLED=1 PORT=8501

EXPOSE 8501
CMD ["npm", "run", "dev"]
