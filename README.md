# feeds-import-worker

Сервис создан для импорта внешних фидов со внешних ресурсов

## Информация о файлах конфигурации
Все конфигурции можно найти в директории:
```bash
src/feeds_importing_worker/config
```

## Информаци о ENV-параметрах
Имеющиеся env-параметры в проекте:
```
APP_POSTGRESQL_NAME=test_name
APP_POSTGRESQL_USER=user
APP_POSTGRESQL_PASSWORD=password
APP_POSTGRESQL_HOST=localhost
APP_POSTGRESQL_PORT=5432

DAGSTER_HOME=~/dagster_home
DAGIT_ENABLED=false
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

Для отладки можно запустить dagit (dagster web UI) установив env DAGIT_ENABLED=true.
В этом случае dagit запуститься на 3000 порту.

Для настроек dagster используется файл /config/dagster.yaml

### Требования к инфраструктуре
1. Минимальная версия Kafka:
  ```yaml
    wurstmeister/kafka:>=2.13-2.7.2
  ```
2. Минимальная версия Postgres:
  ```yaml
    postgres:>=14-alpine
  ```
3. Минимальная версия zookeper:
  ```yaml
    wurstmeister/zookeeper
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
  db:
    image: rshb-cti-db-postgres:staging

  worker:
    restart: always
    build: ./
    ports:
    - "8080:8080"
    environment:
        APP_POSTGRESQL_USER: dbuser
        APP_POSTGRESQL_PASSWORD: test
        APP_POSTGRESQL_NAME: db
        APP_POSTGRESQL_HOST: db
        APP_POSTGRESQL_PORT: 5432
    depends_on:
      - db

networks:
    external:
      name: kafka_net
```

3. Запуск контейнеров:
```bash
docker-compose up --build
```
