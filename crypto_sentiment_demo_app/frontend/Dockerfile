FROM node:16.15.0

WORKDIR /app
COPY package.json ./
COPY ./ ./

RUN npm install --legacy-peer-deps
RUN npm rebuild node-sass

ARG HOST
ENV REACT_APP_HOST=$HOST

RUN npm run build
RUN npm install -g serve
RUN yarn global add serve
