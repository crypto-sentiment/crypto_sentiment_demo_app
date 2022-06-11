FROM node

WORKDIR /app
COPY package.json ./
COPY ./ ./

RUN npm install --legacy-peer-deps

ARG HOST
ENV REACT_APP_HOST=$HOST

RUN npm run build
RUN npm install -g serve
RUN yarn global add serve
