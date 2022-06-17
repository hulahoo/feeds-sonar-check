# feeds-import-worker

Сервис создан для импорта внешних ресурсов Threat Intelligence.

## Test and Deploy

### Для запуска проекта с помощью Docker Compose:

- Скопируйте данный репозиторий
- Переименуйте """example.env""" в """.env.dev""" и измените в нем данные.
- Запустите проект командой """docker compose up -d --build""" (уберите ключ -d если не хотите запускать проект в фоновом режиме)

Проведите миграции базы данных выполнив два последовательных запроса:

- """docker compose exec web python3 manage.py makemigrations"""
- """docker compose exec web python3 manage.py migrate"""

После всех выполненных шагов, создайте учетную запись администратора
"""docker compose exec web python3 manage.py createsuperuser"""
Для взаимодействия с админ панелью перейдите по адресу: """localhost:8000/admin"""

### Для локального запуска в dev среде

- Скопируйте данный репозиторий

Проведите миграции базы данных выполнив два последовательных запроса:

- """python3 threatintel/manage.py makemigrations"""
- """python3 threatintel/manage.py migrate"""

Создайте учетную запись администратора

- """python3 threatintel/manage.py createsuperuser"""

Запустите локальный сервер (только для разработки, будет использована sqlite БД)

- """python3 threatintel/manage.py runserver"""
