# О проекте
Данный проект представляет собой веб-приложение, разработанное с использованием фреймворка Django и интеграцией платежной системы Stripe. Проект позволяет пользователям совершать онлайн-платежи с использованием безопасного и современного API Stripe, что обеспечивает гибкость в обработке как одноразовых платежей, так и подписок.

## Основные возможности
- **Аутентификация и регистрация пользователей:**  
  Реализована система регистрации, входа и управления профилем.
- **Создание и управление заказами:**  
  Пользователи могут формировать заказы и оплачивать их через Stripe.
- **Интеграция с Stripe:**  
  Обработка платежей посредством Stripe API, включая создание сессий оплаты и обработку вебхуков для асинхронного подтверждения транзакций.
- **Поддержка тестового и продакшн режимов:**  
  Возможность легко переключаться между тестовыми и реальными ключами API для безопасного тестирования и запуска.
  
## Технологии
- **Backend:** Python, Django
- **Платежная система:** Stripe API
- **База данных:** PostgreSQL
- **Деплой:** Docker

# Установка и запуск
## Получить ключи для stripe:
* STRIPE_PUBLISHABLE_KEY и STRIPE_SECRET_KEY: https://dashboard.stripe.com/test/apikeys 
* STRIPE_WEBHOOK_SECRET: https://dashboard.stripe.com/test/webhooks

## Запуск через Docker
* **Клонирование репозитория:**
```
git clone https://github.com/MaximOdintsov/django_stripe.git
cd django_stripe
```
* **Создать файл *.env.prod*:**
```
SECRET_KEY=django-insecure-securekey
DEBUG=1
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=your_db_name
SQL_USER=your_db_user
SQL_PASSWORD=your_db_password
SQL_HOST=db
SQL_PORT=5432

ALLOWED_HOSTS=localhost 127.0.0.1 127.0.0.1:1337 0.0.0.0 [::1]
DOMAIN_URL=http://127.0.0.1:1337/
CSRF_TRUSTED_ORIGINS=http://localhost:1337 http://127.0.0.1:1337 [::1]

STRIPE_PUBLISHABLE_KEY=pk_test_yourkey
STRIPE_SECRET_KEY=sk_test_yourkey
STRIPE_WEBHOOK_SECRET=whsec_yourkey
```
* **Создать файл *.env.prod.db*:**
```
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
```
* **Создать файл *.env.stripe_cli*:**
```
STRIPE_API_KEY=sk_test_yourkey
STRIPE_DEVICE_NAME=stripe
```
* **Запустить docker-compose:**
```
docker compose up -d --build
```
* **Авторизоваться и запустить stripeCLI:**
```
docker compose exec stripe stripe login
docker compose exec stripe stripe listen --forward-to 127.0.0.1/webhooks/stripe/
```
* **Создать миграции:**
```
docker compose exec web python3 backend/manage.py migrate
```
* **Создать суперпользователя:**
```
docker compose exec web python3 backend/manage.py createsuperuser
```
* **Собрать статические файлы:**
```
docker compose exec web python3 backend/manage.py collectstatic
```

## Запуск локально на linux:
* **Клонирование репозитория:**
```
git clone https://github.com/MaximOdintsov/django_stripe.git
cd django_stripe
```
* **Создать файл **.env**:**
```
SECRET_KEY=django-insecure-securekey
DEBUG=1
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=your_db_name
SQL_USER=your_db_user
SQL_PASSWORD=your_db_password
SQL_HOST=localhost
SQL_PORT=5432
DOMAIN_URL=http://127.0.0.1:8000/
ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0 [::1]
CSRF_TRUSTED_ORIGINS=http://localhost:8000/ http://127.0.0.1:8000/ [::1]
STRIPE_PUBLISHABLE_KEY=pk_test_yourkey
STRIPE_SECRET_KEY=sk_test_yourkey
STRIPE_WEBHOOK_SECRET=whsec_yourkey
```
* **Создать виртуальное окружение и установить зависимости:**
```
python3 -m pip venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
* **Создать миграции в БД:**
```
cd backend
./manage.py migrate
```
* **Запустить тесты:**
```
./manage.py test orders.tests --failfast
```
* **Создать суперпользователя:**
```
./manage.py createsuperuser
```
* **Авторизоваться и запустить stripeCLI:**
```
./stripe login
./stripe listen --forward-to 127.0.0.1/webhooks/stripe/
```
* **Запустить приложение:**
```
./manage.py runserver
```
