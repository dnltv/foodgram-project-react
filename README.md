[![Django-app workflow](https://github.com/dnltv/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/dnltv/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=5381ff&color=830f00)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=5381ff&color=830f00)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=830f00)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=5381ff&color=830f00)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&color=830f00)](https://jwt.io/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=5381ff&color=830f00)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=5381ff&color=830f00)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=5381ff&color=830f00)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=5381ff&color=830f00)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=5381ff&color=830f00)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=5381ff&color=830f00)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=5381ff&color=830f00)](https://cloud.yandex.ru/)
### Foodgram
The project is available at the [link](http://84.252.128.110).
To log in as a `superuser` enter: 
```
email: admin@mail.ru
password: admin12345
```

### Description
Service for __publishing__ and __sharing__ `Recipes`. 

Authorized `Users` can __subscribe__ to `Authors` they like, __add__ `Recipes` to `Favorites`, __save__ them to a `ShoppingCart` and __upload__ a shopping list.
Unauthorized `Users` can __register__, __log in__, and __view__ other users' `Recipes`.




### Technology Stack
- Python 3.9
- Django 3.2.18
- Django REST Framework 3.14
- PostgreSQL 13.0
- Nginx 1.21.3
- Docker Compose

Full list in the file **requirements.txt**

### Preparing for launch
- Clone the repository and go to it on the command line.
```bash
git clone https://github.com/dnltv/foodgram-project-react
cd foodgram-project-react
```

- Install and activate the virtual environment taking into account the Python 3.7 version (choose python at least 3.7):

For Linux / MacOS:
```bash
python3.7 -m venv venv
```

```bash
. venv/bin/activate
```

For Windows:
```bash
py -3.7 -m venv venv
```

```bash
source venv/Scripts/activate
```

- Install all dependencies from the file **requirements.txt**

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Environment variables
- Create `.env` file in the `infra` directory according to the following pattern
```bash
nano infra/.env
```

```
DJANGO_TOKEN=YOUR_TOKEN
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
DB_HOST=db
DB_PORT=5432
```

[Project link](http://84.252.128.110)


### Workflow

- `tests` - Checking the code for compliance with the PEP8 standard (using the flake8 package) and running py test. Further steps will be performed only if the push was in the master or main branch.
- `build_and_push_to_docker_hub` - Build and push docker images to Docker Pub.
- `deploy` - Automatic deployment of the project to the production server. Files are being copied from the repository to the server.
- `send_message` - Sending a notification to Telegram.

### Set GH Actions Secrets
```
DOCKER_USERNAME - user name in DockerHub
DOCKER_PASSWORD - password in DockerHub
HOST - server ip address
USER - user on server
SSH_KEY - private ssh-key (public must be on the server)
PASSPHRASE - the passphrase for the ssh key
DB_ENGINE - django.db.backends.postgresql
DB_HOST - db
DB_PORT - 5432
DB_NAME - postgres (by default)
POSTGRES_USER - postgres (by default)
POSTGRES_PASSWORD - postgres (by default)
DJANGO_TOKEN - django application secret key
ALLOWED_HOSTS - list of allowed hosts
TELEGRAM_TO - the id of your telegram account (you can find out from @userinfobot, the /start command)
TELEGRAM_TOKEN - bot token (you can get a token from @BotFather, /token, bot name)
```

### Preparing Ubuntu server
- Update and upgrade packages
```bash
sudo apt update && apt upgrade -y
```

- Install Docker
```bash
sudo apt install curl
sudo curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```
- Copy `nginx/default.conf` to server from your local machine (Command from the root directory of the project).
```bash
scp -r infra/nginx.conf <username>@<host>:/home/<username>/
```
- Copy `docker-compose.yaml` to server from your local machine (Command from the root directory of the project).
```bash
scp infra/docker-compose.yml <username>@<host>:/home/<username>/
```

- Perform migrations on server:
```bash
sudo docker compose exec backend python manage.py migrate
```
- Collect project static:
```bash
sudo docker compose exec backend python manage.py collectstatic --no-input
```
- Create a `superuser`:
```bash
sudo docker compose exec backend python manage.py createsuperuser
```
- If necessary, fill in the database with test data with the command:
```bash
sudo docker compose exec backend python manage.py json_to_db --path 'recipes/data/tags.json'
```
```bash
sudo docker compose exec backend python manage.py json_to_db --path 'recipes/data/ingredients.json'
```
```bash
sudo docker compose exec backend python manage.py json_to_db --path 'recipes/data/users.json'
```

- Stop containers:
```bash
sudo docker compose down -v
```

### Author:
- [Danil Treskov](https://github.com/dnltv)
