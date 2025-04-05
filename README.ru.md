# vHub

**Описание**

<p>Это приложение предназначено для публикации видео файлов в интранете. Настоятельно рекомендую использовать в docker контейнере.<p>

## Возможности

- Доступ к видео файлам не авторизованным\не зарегистрированным пользователя.
- Разграничение доступа к видео файлам средствами "Groups" и "Playlists".
- Ручная установка пароля пользователям.
- Генерация приложением пароля и отправка его на почту пользователю(если включена почта).
- Добавление пользователей\видео в "Groups" и "Playlists".
- Скрипт удаления видео remove_video.py.
- Swagger доступен на /swagger.

## Docker-compose

Готовый docker-compose файл находится в каталоге docker.

Создайте каталоги.

```bash
mkdir -p /opt/{vhub-nginx,vhub-data-minio,vhub-data-mysql,vhub-app/logs} /opt/vhub-nginx/{ssl,conf.d}
chown -R 1001:1001 /opt/vhub-data-minio
```

В каталоге /opt/vhub-nginx/conf.d создайте файл vhub.conf
с содержимым.
```
server {
  listen 80;
  server_name vhub;

  client_max_body_size 0;
  server_tokens off;

  set $app 172.28.1.2:3000;
  set $minio 172.28.1.3:9000;

  ignore_invalid_headers off;
  proxy_buffering off;
  proxy_request_buffering off;

  location /vhub/ {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 300;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    chunked_transfer_encoding off;

    proxy_pass http://$minio;
  }

  location / {
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_pass http://$app;
  }
}
```

Если вам нужен https разместите свой SSL сертификат в каталог /opt/vhub-nginx/ssl.

```
server {
  listen 80;
  server_name vhub;
  return 301 https://$host$request_uri;
}

server {
  listen 443 ssl;
  server_name vhub;
  client_max_body_size 0;
  server_tokens off;

  set $app 172.28.1.2:3000;
  set $minio 172.28.1.3:9000;

  ignore_invalid_headers off;
  proxy_buffering off;
  proxy_request_buffering off;

  ssl_certificate /etc/nginx/ssl/<SSL-CRT>;
  ssl_certificate_key /etc/nginx/ssl/<SSL-KEY>;

  location /vhub/ {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 300;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    chunked_transfer_encoding off;

    proxy_pass http://$minio;
  }

  location / {
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_pass http://$app;
  }
}
```

## Environment

Для приложения доступны переменные окружения.

Значения по умолчанию:

- VHUB_SHARED_VIDEO=false
- VHUB_SHARED_VIDEO_TIME=7
- VHUB_EMAIL=false
- VHUB_ADMIN_NAME=admin
- VHUB_ADMIN_PWD=vhub
- VHUB_MINIO_USER=vhub-minio
- VHUB_MINIO_PWD=vhub-minio
- VHUB_MINIO_PORT=9000
- VHUB_MINIO_BUCKET=vhub
- VHUB_MINIO_SRV=172.28.1.3
- VHUB_MYSQL_SRV=172.28.1.4
- VHUB_MYSQL_USER=root
- VHUB_MYSQL_PWD=vhub-mysql
- VHUB_MYSQL_PORT=3306
- VHUB_MYSQL_DB=vhub
- VHUB_SMTP_SRV=""
- VHUB_SMTP_PORT=""
- VHUB_SMTP_USER=""
- VHUB_SMTP_PWD=""

**VHUB_SHARED_VIDEO** - Возможность поделиться видеофайлом (в том числе для не зарегистрированных пользователей).

**VHUB_SHARED_VIDEO_TIME** - Временной отрезок предоставляющий общий доступ к видео файлу.

**VHUB_EMAIL** - Доступность функционала электронный почты (отправка\сброс паролей пользователей).

**VHUB_ADMIN_NAME** - Имя админа.

**VHUB_ADMIN_PWD** - Пароль админа.

**VHUB_MINIO_USER** - Соответствие MINIO_ROOT_USER в docker-compose.yml.

**VHUB_MINIO_PWD** - Соответствие MINIO_ROOT_PWD в docker-compose.yml.

**VHUB_MINIO_PORT** - Minio порт(по умолчанию - 9000).

**VHUB_MINIO_BUCKET** - Соответствие MINIO_DEFAULT_BUCKETS в docker-compose.yml.

**VHUB_MINIO_SRV** - Соответствие ip адресу Minio в docker-compose.yml.

**VHUB_MYSQL_SRV** - Соответствие ip адресу MySQL в docker-compose.yml.

**VHUB_MYSQL_USER** - MySQL пользователь(по умолчанию - root).

**VHUB_MYSQL_PWD** - Соответствие MYSQL_ROOT_PASSWORD в docker-compose.yml.

**VHUB_MYSQL_PORT** - MySQL порт(по умолчанию - 3306).

**VHUB_MYSQL_DB** - Генерация новой базы данных с заданным именем.

**VHUB_SMTP_SRV** - Адрес smtp сервера(по умолчанию - "").

**VHUB_SMTP_PORT** - Порт smtp сервера(по умолчанию - "").

**VHUB_SMTP_USER** - Пользователь smtp сервера(по умолчанию - "").

**VHUB_SMTP_PWD** - Пароль пользователя smtp сервера(по умолчанию - "").

## Сборка Docker образа

```bash
docker build --no-cache -t vhub:latest --file docker/Dockerfile .
```

## Удалить видео
```bash
docker exec -it vhub-app python3 utils/remove_video.py -h
```
1. Удалить одно видео. ID видео получить из адресной строки браузера, например, `http://192.168.0.2/video/92ec9932-6a9e-476d-8208-017dbf0185a4.mp4`, где `92ec9932-6a9e-476d-8208-017dbf0185a4.mp4` - ID видео.
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --id 92ec9932-6a9e-476d-8208-017dbf0185a4.mp4 --type single
    ```
2. Удалить массово для группы, плейлиста, пользователя.
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --type user --type-name admin
    ```
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --type group --type-name default
    ```
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --type playlist --type-name default
    ```
3. Удалить выборочно, по списку в файле. Создать файл. Наполнить его ID видео которые необходимо удалить. Скопировать в контейнер.
    ```bash
    echo "2ec9932-6a9e-476d-8208-017dbf0185a4.mp4" > delete-video
    docker cp delete-video vhub-app:/app/delete-video
    docker exec -it vhub-app python3 utils/remove_video.py --file /app/delete-video
    ```

## Скриншоты

![login](images/login.png)

![admin](images/admin.png)

![admin_panel](images/admin_panel.png)

![users](images/users.png)

![video](images/video.png)

![video_play](images/video_play.png)

![swagger](images/swagger.png)