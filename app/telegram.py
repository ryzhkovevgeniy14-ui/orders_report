import requests


def send_telegram_message(bot_token, chat_id, message):
    """
    Отправляет текстовое сообщение через Telegram Bot API.
    """
    # Формируем URL Telegram Bot API
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        # Отправляем сообщение в указанный чат
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message,
            },
            timeout=10,
        )

        # Вызываем исключение при HTTP-ошибке
        response.raise_for_status()

    except requests.RequestException as error:
        # Преобразуем ошибку requests в исключение уровня приложения
        raise RuntimeError(
            f"Не удалось отправить Telegram-уведомление: {error}"
        ) from error


def notify_telegram(bot_token, chat_id):
    """
    Формирует и отправляет уведомление об успешном создании отчёта.
    """
    # Формируем краткое сообщение
    message = "✅ Отчёт успешно сформирован"

    send_telegram_message(bot_token, chat_id, message)