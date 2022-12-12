# feeds-import-worker

Сервис создан для импорта внешних ресурсов Threat Intelligence.

### Запуск воркера

1. Скопируйте данный репозиторий

2. Создайте виртуальное окружение
```
python3 -m .venv venv
```

3. Активировать виртуальное окружение: 
```
source .venv/bin/activate
```
4. Установить зависимости: 
```
pip3 install -r requirements.txt
```
5. Запустите сервер
```
- dagit -f main.py 
```
появится веб интерфейс и по нему можно запустить задачи


## Информаци о ENV-параметрах
Имеющиеся env-параметры в проекте:
```
SQL_DATABASE=
SQL_USER=
SQL_PASSWORD=
SQL_HOST=
SQL_PORT=
```
