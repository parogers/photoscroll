
FROM node:latest AS client-build

COPY client/package.json /home/node/
COPY client/package-lock.json /home/node/
WORKDIR /home/node/
RUN npm ci
COPY client /home/node/
RUN npm run build


FROM nginx:latest

COPY docker/nginx/api.conf /etc/nginx/conf.d
COPY --from=client-build /home/node/dist /usr/share/nginx/html
