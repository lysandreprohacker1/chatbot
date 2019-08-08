Production deployment
=====================

First, install the prerequisites system (we assume Debian or Ubuntu here):

```bash
apt-get install build-essential python3-dev python3-pip python3-venv
apt-get install postgresql
```

In production, you should create a dedicated user teh application. All steps for the installation, which do not need root access, should be done using this user. We assume this user is called `chatbot`, it’s home is `/srv/chatbot` and the application is located in `/srv/chatbot/chatter_bot`. The user can be created using:

```bash
# as root
useradd -u 2000 -c 'Chatbot' -s /bin/bash -d /srv/chatbot -m chatbot
```

Using this user, create a virtual env in the home of this user:

```bash
# as chatbot
python3 -m venv env

echo "source ~/env/bin/activate" >> ~/.bashrc
. ~/.bashrc
```

Clone the repository and change directory and install the production dependencies:

```bash
# as chatbot
git clone https://github.com/MagdaN/chatter_bot chatter_bot
cd chatter_bot
```

Install production dependencies:

```bash
# as chatbot
pip install -r requirements/prod.txt
```

Create `/srv/chatbot/chatter_bot/.env` with the folowing content:

```bash
DJANGO_SECRET_KEY=<a long random secret key>
DJANGO_DEBUG=False
DJANGO_PSQL_DBNAME=chatbot
```

Create the database user and the database:

```bash
# as postgres user
createuser chatbot
createdb chatbot --owner=chatbot
```

Run the database migrations:

```bash
# as chatbot
./manage.py migrate
```

Train the bot:

```bash
# as chatbot
./manage.py train
```

#### Front end

If nodejs is not desired on the prodction system, you can also perform the following steps on a different machine and copy the `/static` directory to `/srv/chatbot/chaterbot` on the server.

Install [nvm](https://github.com/nvm-sh/nvm) for the `chatbot` user:

```bash
# as chatbot
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.bashrc
```

Install the front-end dependencies and build the static files using:

```bash
# as chatbot
nvm install
npm install
npm run build:prod
```

#### Gunicorn setup

Install gunicorn:

```bash
# as chatbot
pip install -r requirements/gunicorn.txt
```

Systemd will launch the Gunicorn process on startup and keep running. Create a new systemd service file (you will need root/sudo permissions for that):

```
# /etc/systemd/system/chatbot.service
[Unit]
Description=Chatbot gunicorn daemon
After=network.target

[Service]
User=chatbot
Group=chatbot
WorkingDirectory=/srv/chatbot/chatter_bot
EnvironmentFile=/srv/chatbot/chatter_bot/.env
ExecStart=/srv/chatbot/env/bin/gunicorn --bind unix:/tmp/chatbot.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

This service needs to be started and enabled like any other service:

```bash
# as root
systemctl daemon-reload
systemctl start chatbot
systemctl enable chatbot
systemctl status chatbot
```

#### NGINX

Next, install NGINX:

```bash
# as root
sudo apt-get install nginx
```

Crate the Nginx configuration as follows (again with root/sudo permissions):

```
# /etc/nginx/sites-available/YOURDOMAIN
server {
    listen 80;
    server_name YOURDOMAIN;

    access_log /var/log/nginx/YOURDOMAIN.access.log;
    error_log /var/log/nginx/YOURDOMAIN.error.log;

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_pass http://unix:/tmp/chatbot.sock;
    }
    location /static/ {
        alias /srv/chatbot/chatter_bot/static_root/;
    }
}
```

Enable the site:

```bash
# as root
ln -s /etc/nginx/sites-available/YOURDOMAIN /etc/nginx/sites-enabled/YOURDOMAIN
nginx -t
systemctl reload nginx
```

The application should now be available on YOURDOMAIN. Note that the unix socket needs to be accessible by NGINX.

As you can see from the virtual host configurations, the static assets such as CSS and JavaScript files are served independently from the reverse proxy to the gunicorn process. In order to do so they need to be gathered in the `static_root` directory. This can be achieved by running:

```bash
# as chatbot
python manage.py collectstatic
```

#### Let's Encrypt

Install the NGINX intergration:

```bash
# as root
apt-get install python3-certbot-nginx
certbot --nginx -d YOURDOMAIN
```

And follow the questions. Thats it.