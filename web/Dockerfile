FROM node

WORKDIR /tmp/
ADD package.json ./
ADD package-lock.json ./
RUN npm install

RUN mkdir -p /app
WORKDIR /app
RUN webpack

