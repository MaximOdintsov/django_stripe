FROM nginx:1.23.3-alpine
RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir -p etc/nginx/cache/
COPY nginx.conf /etc/nginx/conf.d
