# The whole site is static files, so this is nginx and nothing else.
# web/ is the docroot -- which is why web/data/ holds the JSON the pages fetch.
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY web/ /usr/share/nginx/html/

# Lessons are plain JSON fetched by the page; make sure nginx says so.
RUN echo "ok" > /usr/share/nginx/html/healthz
