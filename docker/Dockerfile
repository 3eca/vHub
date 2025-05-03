FROM python:3.10-alpine3.20

LABEL maintainer="https://github.com/3eca" \
      version="1.1.0" \
      description="Application for posting video files to the intranet"

COPY . /app

WORKDIR /app

RUN apk add --no-cache ffmpeg && \
    pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    mv fix/flask-sqlalchemy-issues-1168/extension.py fix/flask-sqlalchemy-issues-1168/pagination.py /usr/local/lib/python3.10/site-packages/flask_sqlalchemy/ && \
    mv fix/moviepy-issues-2002/resize.py /usr/local/lib/python3.10/site-packages/moviepy/video/fx/ && \
    rm -fr fix

EXPOSE 3000

CMD ["./run.sh"]