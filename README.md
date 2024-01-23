# praktikum_new_diplom

ip: 158.160.82.152

https://foodgramfoodgram.ddns.net/

login: 8815585@gmail.com
//
pass: xxxxxx


# Foodgram

![Master Foodgram workflow](https://github.com/Dmitry8815585/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Foodgram - сервис для публикации рецептов.

## Описание

Основная идея проекта заключается в запуске проекта Foodgram в контейнерах с 

автоматическим тестированием и деплоем этого проекта на удалённый сервер.

## Требования

Прежде чем начать, убедитесь, что у вас установлены следующие инструменты:

- Docker: [установка Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [установка Docker Compose](https://docs.docker.com/compose/install/)
- Node.js: [установка Node.js](https://nodejs.org/)


## Установка

Нужно скопировать содержимое .env.example в локальный файл .env и проставить нужные значения вместо CHANGE_ME

1. Клонировать репозиторий:

    git clone https://github.com/good8815585/foodgram-project-react
.git
    cd foodgram-project-react


2. Установить зависимости бэкенда:

    docker-compose -f docker-compose.production.yml run backend python manage.py migrate

3. Установить зависимости фронтенда:

    docker-compose -f docker-compose.production.yml run frontend npm install

4. Собрать статические файлы и собрать Docker-образы:

    docker-compose -f docker-compose.production.yml build

## Запуск


Запустить Docker-контейнеры:

    docker-compose -f docker-compose.production.yml up -d

        Провести миграции и собрать статические файлы:

            docker-compose -f docker-compose.production.yml exec backend python manage.py migrate
            docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic
            docker-compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/



## Деплой

    Проект автоматически деплоится при пуше в ветку master с использованием GitHub Actions.
    После успешного выполнения придет сообщение в Telegram.


## Примеры запросов (документация к проекту).

[документация](https://foodgramfoodgram.ddns.net/api/docs/redoc.html)
