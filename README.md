# Дипломная работа Foodgram
[![Foodgram CI/CD](https://github.com/cra1ger51/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/cra1ger51/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

_________________________________________________
## Описание
Собрание разнообразных рецептов.

### Foodgram - возможности:

- Просмотреть список рецептов
- Добавлять рецепты в избранное
- Подписываться на авторов
- Собирать список покупок с выводом в PDF
- Обладает удобным API-интерфейсом
 
_____________________________________________________

## Техническое описание

> Развернутый проект расположен по адресу 
```
http://158.160.52.119/
```
> Документация к APi доступна по адресу: 
```
http://158.160.52.119/api/docs/
```
> Админ-панель(login: admin, password: admin): 
```
http://158.160.52.119/admin/
```

### Примененные технологии
 > Python 3.7.9
 > Django 3.2.18
 > djangorestframework 3.14.0
 > gunicorn 20.1.0
 > reportlab 4.0.4

### Шаблон наполнение .env:

DJANGO_KEY=django-insecure-9$xw0k2rx4p6v1_itc8fqg%m^p8%_z_o4x$m*gpet*o!-az6h2
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

### Как запустить проект:

набор команд для запуска приложения в контейнерах:
```
docker-compose up -d --build
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input 
```

Наполнение базы ингредиентами из CSV:

```
docker-compose exec web python manage.py basefill
```
______________________________________
### Автор
Даниил Алексеенко(https://github.com/cra1ger51)


### Лицензия
BSD 3-Clause License