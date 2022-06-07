FROM node

WORKDIR /app
COPY package.json ./
COPY ./ ./

RUN npm install --legacy-peer-deps
RUN npm rebuild node-sass
