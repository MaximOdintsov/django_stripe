# Для запуска docker-compose:
! При этом варианте вебхук не привязывает пользователя к заказу
* Создать файл **.env.prod**:
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
* Создать файл **.env.prod.db**:
```
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
```
* Создать файл **.env.stripe_cli**:
```
STRIPE_API_KEY=sk_test_yourkey
STRIPE_DEVICE_NAME=stripe
```
* Запустить docker-compose:
```
~/test_django_stripe$ docker-compose up -d --build
```
* Авторизоваться и запустить stripeCLI:
```
~/test_django_stripe$ docker-compose exec stripe stripe login
~/test_django_stripe$ docker-compose exec stripe stripe listen --forward-to 127.0.0.1/webhooks/stripe/
```
* Создать миграции:
```
~/test_django_stripe$ docker-compose exec web python3 backend/manage.py migrate
```
* Создать суперпользователя:
```
~/test_django_stripe$ docker-compose exec web python3 backend/manage.py createsuperuser
```
* Собрать статические файлы:
```
~/test_django_stripe$ docker-compose exec web python3 backend/manage.py collectstatic
```

# Для локальной разработки:
* Создать файл **.env**:
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
* Активировать виртуальное окружение
* Установить зависимости из [requirements.txt](requirements.txt)
* Создать миграции:
```
~/test_django_stripe$ python3 backend/manage.py migrate
```
* Запустить тесты:
```
~/test_django_stripe$ python3 backend/manage.py test orders.tests --failfast
```
* Создать суперпользователя:
```
~/test_django_stripe$ python3 backend/manage.py createsuperuser
```
* Авторизоваться и запустить stripeCLI:
```
~/test_django_stripe$ backend/stripe login
~/test_django_stripe$ backend/stripe listen --forward-to 127.0.0.1/webhooks/stripe/
```
* Запустить приложение:
```
~/test_django_stripe$ python3 backend/manage.py runserver
```

## Где взять ключи:
* STRIPE_PUBLISHABLE_KEY и STRIPE_SECRET_KEY: https://dashboard.stripe.com/test/apikeys 
* STRIPE_WEBHOOK_SECRET: https://dashboard.stripe.com/test/webhooks

### Недоработки:
* При создании заказа через вебхук stripe, в заказ не добавляются orderitem
* При развертывании приложения через докер, вебхук не привязывает пользователя к заказу