# API-Shop

## Описание

API-Shop — это REST API для заказа товаров с их склада. В системе предусмотрены три роли пользователей: Гость, Клиент и Администратор.

## Структура проекта

- **deploy/**: Содержит `docker-compose.yml` для развертывания контейнеров.
- **project/**: Веб-приложение на Flask.
- **collection/**: Экспортированная Postman коллекция с примерами запросов.
- **README.md**: Инструкция по запуску и использованию проекта.

## Требования

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/0ldb3R/api-shop.git
cd api-shop/deploy
