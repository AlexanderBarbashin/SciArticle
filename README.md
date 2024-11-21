# Чат


## О проекте

Проект представляет собой веб приложение, разработанное на фреймворке FastAPI. Реализует чат, в котором пользователи
могут обмениваться сообщениями.

## Особенности

* Возможность отправки уведомлений через POST эндпоинт
* Передача уведомлений с помощью брокера сообщений
* Получение уведомлений в комнатах из двух пользователей

## Использованные технологии

* Python 3
* FastAPI
* SQLAlchemy - ORM
* Alembic - Создание и применение миграций
* FastStream - интеграция RabbitMQ с FastAPI
* Pika - подключение к RabbitMQ из Python для создания очереди
* PostgreSQL - СУБД
* Docker Compose - поднятие контейнеров с PostgreSQL и RabbitMQ

## Подготовка и запуск

Для развертывания проекта на удаленном сервере необходимо:

### Общие требования:

* Установить Docker (если установка не была выполнена ранее)
* Склонировать проект на удаленный репозиторий: **git clone**
* Перейти в папку проекта: **cd SciArticle**
* Создать файл .env по образцу (файл .env.template), установить необходимые env опции
* Запустить контейнеры **docker compose up -d**
* Установить зависимости **pip install -r requirements.txt**
* Применить миграции **alembic upgrade head**
* Запустить приложение **python3 src.main.py**