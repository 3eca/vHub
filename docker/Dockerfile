FROM python:3.10-alpine3.20

LABEL maintainer="https://github.com/3eca" \
      version="1.0.0" \
      description="Application for posting video files to the intranet"

COPY . /app

WORKDIR /app

RUN apk add --no-cache ffmpeg && \
    pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    mv fix/flask-sqlalchemy-issues-1168/extension.py fix/flask-sqlalchemy-issues-1168/pagination.py /usr/local/lib/python3.10/site-packages/flask_sqlalchemy/ && \
    mv fix/moviepy-issues-2002/resize.py /usr/local/lib/python3.10/site-packages/moviepy/video/fx/ && \
    rm -fr fix

ENV VHUB_SHARED_VIDEO=false \
    VHUB_SHARED_VIDEO_TIME=7 \
    VHUB_EMAIL=false \
    VHUB_ADMIN_NAME=admin \
    VHUB_ADMIN_PWD=vhub \
    VHUB_MINIO_USER=vhub-minio \
    VHUB_MINIO_PWD=vhub-minio \
    VHUB_MINIO_PORT=9000 \
    VHUB_MINIO_BUCKET=vhub \
    VHUB_MINIO_SRV=172.28.1.3 \
    VHUB_MYSQL_SRV=172.28.1.4 \
    VHUB_MYSQL_USER=root \
    VHUB_MYSQL_PWD=vhub-mysql \
    VHUB_MYSQL_PORT=3306 \
    VHUB_MYSQL_DB=vhub \
    VHUB_SMTP_SRV="" \
    VHUB_SMTP_PORT="" \
    VHUB_SMTP_USER="" \
    VHUB_SMTP_PWD=""

EXPOSE 3000

ENTRYPOINT ["python3", "main.py"]