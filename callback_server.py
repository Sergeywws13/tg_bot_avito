from flask import Flask, request
import logging
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/callback")
def callback():
    """
    Обрабатывает запрос от API Авито после авторизации.
    """
    code = request.args.get("code")
    if code:
        logger.info(f"Получен код авторизации: {code}")
        

        try:
            response = requests.post(
                "http://localhost:5000/handle_callback",  # URL вашего бота
                json={"code": code}
            )
            if response.status_code == 200:
                return "Авторизация успешна! Код передан боту."
            else:
                return "Ошибка при передаче кода боту.", 500
        except Exception as e:
            logger.error(f"Ошибка при отправке кода боту: {e}")
            return "Ошибка при отправке кода боту.", 500
    else:
        logger.error("Код авторизации не найден в запросе.")
        return "Ошибка: код авторизации отсутствует.", 400

if __name__ == "__main__":
    app.run(port=8000)
