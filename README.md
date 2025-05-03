# vHub

**Description**

<p>This application is designed to publish video files to the intranet. I strongly recommend using it in a docker container.<p>

## Capabilities

- Access to video files by unauthorized/unregistered users.
- Restrict access to video files by means of “Groups” and “Playlists”.
- Manual password setting for users.
- Generating a password by the application and sending it to the user's e-mail (if mail is enabled).
- Adding video users to “Groups” and “Playlists”.
- Video removal script remove_video.py.
- Swagger is available at /swagger.
- LDAP.

## Docker-compose

The ready docker-compose file is located in the docker directory.

Create the directories.

```bash
mkdir -p /opt/{vhub-nginx,vhub-data-minio,vhub-data-mysql,vhub-app/logs} /opt/vhub-nginx/{ssl,conf.d}
chown -R 1001:1001 /opt/vhub-data-minio
```

In the /opt/vhub-nginx/conf.d directory, create the vhub.conf file
with the contents.

```
server {
  listen 80;
  server_name vhub;

  client_max_body_size 0;
  server_tokens off;

  set $app 172.28.1.4:3000;
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

If you need https place your SSL certificate in the /opt/vhub-nginx/ssl directory.

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

  set $app 172.28.1.4:3000;
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

## Build Docker image

```bash
docker build --no-cache -t vhub:latest --file docker/Dockerfile .
```

## Delete video
```bash
docker exec -it vhub-app python3 utils/remove_video.py -h
```
1. Delete one video. Get the video ID from the browser address bar, for example, `http://192.168.0.2/video/92ec9932-6a9e-476d-8208-017dbf0185a4.mp4`, where `92ec9932-6a9e-476d-8208-017dbf0185a4.mp4` is the video ID.
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --id 92ec9932-6a9e-476d-8208-017dbf0185a4.mp4 --type single
    ```
2. Delete in bulk for group, playlist, user.
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --type user --type-name admin
    ```
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --type group --type-name default
    ```
    ```bash
    docker exec -it vhub-app python3 utils/remove_video.py --type playlist --type-name default
    ```
3. Delete selectively, by list in the file. Create a file. Fill it with IDs of videos to be deleted. Copy it to the container.
    ```bash
    echo "2ec9932-6a9e-476d-8208-017dbf0185a4.mp4" > delete-video
    docker cp delete-video vhub-app:/app/delete-video
    docker exec -it vhub-app python3 utils/remove_video.py --file /app/delete-video
    ```

## Screenshots

![login](images/login.png)

![admin](images/admin.png)

![admin_panel](images/admin_panel.png)

![users](images/users.png)

![video](images/video.png)

![video_play](images/video_play.png)

![swagger](images/swagger.png)