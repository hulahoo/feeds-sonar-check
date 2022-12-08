from src.web.app import app


@app.route('/health/readiness', methods=["GET"])
def healthcheck():
    """
    Текущее состояние готовности сервиса
    """
    return 200


@app.route('/health/liveness', methods=["GET"])
def liveness():
    """
    Возвращает информацию о работоспособности сервиса
    """
    return 200
