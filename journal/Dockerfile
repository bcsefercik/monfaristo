FROM node:18-alpine

WORKDIR /app

COPY ./journal/package.json ./

RUN npm install

COPY ./journal/ ./

CMD ["npm", "run", "dev"]
