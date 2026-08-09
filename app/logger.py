import logging


def setup_logger():
    """
    Настраивает логирование приложения и возвращает логгер.

    Логи записываются в файл app.log с указанием времени,
    уровня сообщения и текста события.
    """
    # Настраиваем общий формат и файл для записи логов
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )

    return logging.getLogger(__name__)