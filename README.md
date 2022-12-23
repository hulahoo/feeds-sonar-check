# feeds-import-worker

Сервис создан для импорта внешних фидов со внешних ресурсов

## Информация о файлах конфигурации
Все конфигурции можно найти в директории:
```bash
src/events_gateway/config
```

## Информаци о ENV-параметрах
Имеющиеся env-параметры в проекте:
```
APP_POSTGRESQL_NAME=
APP_POSTGRESQL_USER=
APP_POSTGRESQL_PASSWORD=
APP_POSTGRESQL_HOST=
APP_POSTGRESQL_PORT=
```


### Запуск воркера

1. Создайте виртуальное окружение

```bash
python3 -m venv venv
```

2. Активировать виртуальное окружение: 

```bash
source venv/bin/activate
```

3. Установить зависимости: 

```bash
pip3 install -r requirements.txt
```

4. Собрать приложение как модуль:

```bash
python3 -m pip install .
```

5. Запусить приложение:
```bash
feeds-importing-worker
```

### Запуск с помощью Dockerfile


1. Dockerfile:
```dockerfile
FROM python:3.10.8-slim as deps
WORKDIR /app
COPY . ./
RUN apt-get update -y && apt-get -y install gcc python3-dev
RUN pip --no-cache-dir install -r requirements.txt 
RUN pip --no-cache-dir install -r requirements.setup.txt 
RUN pip install -e .

FROM deps as build
ARG ARTIFACT_VERSION=local
RUN python setup.py sdist bdist_wheel
RUN ls -ll /app/
RUN ls -ll /app/dist/


FROM python:3.10.8-slim as runtime
COPY --from=build /app/dist/*.whl /app/
RUN apt-get update -y && apt-get -y install gcc python3-dev
RUN pip --no-cache-dir install /app/*.whl
ENTRYPOINT ["feeds-importing-worker"]
```

2. docker-compose.yml
```yaml
version: '3'

services:
  postgres_db:
    image: postgres:13.8-alpine
    container_name: db
    restart: unless-stopped
    expose:
      - 5432 
    environment:
        POSTGRES_DB: db
        POSTGRES_USER: dbuser
        POSTGRES_PASSWORD: test

  worker:
    restart: always
    build: ./
    ports:
    - "8080:8080"
    environment:
        APP_POSTGRESQL_USER: dbuser
        APP_POSTGRESQL_PASSWORD: test
        APP_POSTGRESQL_NAME: db
        APP_POSTGRESQL_HOST: postgres_db
        APP_POSTGRESQL_PORT: 5432
    depends_on:
      - postgres_db

networks:
    external:
      name: kafka_net
```

3. Запуск контейнеров:
```bash
docker-compose up --build
```

4. Применить дамп файла для бд в контейнере:
```bash
cat restore.sql | docker exec -i db psql -U dbuser -d db
```

5. Перзапустить контейнер worker

## Накатка миграций происходит во время запуска консольной команды feeds-importing-worker.