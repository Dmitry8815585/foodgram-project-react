# praktikum_new_diplom

ip: 158.160.82.152

https://foodgramfoodgram.ddns.net/

login: xxxxxxxxxxxx
//
pass: xxxxxx


# Foodgram

![Master Foodgram workflow](https://github.com/Dmitry8815585/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Foodgram - сервис для публикации рецептов.
Сайт для публикации рецептов с возможностью добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Написал весь бэкенд включая api. Разместил проект на виртуальном сервере. 
    Стек проекта: Python, Django, DRF, React (basics), Gunicorn, JWT, Postman, PostgreSQL, Docker, Nginx, Git, CI&CD
    В ходе работы над проектом мною было сделано:
1.	Настроил взаимодействие Python-приложения с внешними API-сервисами;
2.	Создал собственный API-сервис на базе проекта Django;
3.	Подключил SPA к бэкенду на Django через API;
4.	Создал образы и запустил контейнеры Docker;
5.	Создал, развернул и запустил на сервере мультиконтейнерные приложения;
6.	Настроил автоматизацию развёртывания проекта (CI&CD) 


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
