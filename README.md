![foodgram workflow](https://github.com/DmitryTok/foodgram-project-react/actions/workflows/main.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
# foodgram-project-react
Application "Product Assistant": a site, on applications you can publish recipes, add other people's recipes to your favorites and subscribe to publications of other authors. The Shopping List service allows users to create a list of products that are needed to prepare selected dishes.

# Run the project
## Clone repository to your computer
```
HTTPS - https://github.com/DmitryTok/foodgram-project-react.git
SSH - git@github.com:DmitryTok/foodgram-project-react.git
GitHub CLI - gh repo clone DmitryTok/foodgram-project-react
```
## Create and feel the .env file
```
DB_ENGINE=<...> # specify that we work with postgresql data base
DB_NAME=<...> # data base name
POSTGRES_USER=<...> # login for connecting to data base
POSTGRES_PASSWORD=<...> # password for connection to data base (create your own)
DB_HOST=<...> # name of the servise (container)
DB_PORT=<...> # port for conection to data base
SECRET_KEY=<...> # kay from settings.py
```
## 1.Assembly and run the container from "infra" folder
```
docker-compose up -d --build
```
## 2.Make migrations
```
docker-compose exec backend python manage.py migrate
```
## 3.Create a Django superuser
```
docker-compose exec backend python manage.py createsuperuser
```
## 4.Collect static
```
docker-compose exec backend python manage.py collectstatic --no-input
```
## 5.Load data to database
```
docker-compose exec backend python manage.py loaddata ingredients.json
```
***
### Example of API request:

Request for recipes:
```python
import requests
from pprint import pprint
url = 'http://127.0.0.1/api/recipes/'
request = requests.get(url).json()
pprint(request)
```
## Progect author:
* https://www.linkedin.com/in/dmitry-tokariev-86b182157
***
## Technology

- Python 3
- Django
- Django REST Framework
- Simple JWT