import os
from collections import Counter

import pandas as pd

from app.excel_writer import create_report_file
from app.logger import setup_logger
from app.processor import process_row
from app.report import build_report
from app.telegram import notify_telegram


logger = setup_logger()


REQUIRED_COLUMNS = [
    "ID заказа",
    "Статус заказа",
    "Дата",
    "Сумма",
    "Мастер",
    "Город",
    "Рекламация",
    "Фото загружено",
]


def find_duplicate_ids(df):
    """
    Находит все строки с дублирующимися ID заказов.

    Используется keep=False, чтобы отметить все строки,
    содержащие один и тот же ID заказа, включая первое появление.
    """
    duplicate_mask = df["ID заказа"].duplicated(keep=False)

    return df[duplicate_mask]


def add_error(errors, row, error_message, excel_row):
    """
    Добавляет ошибочную строку в список ошибок.
    """
    result = row.copy()
    result["Причина ошибки"] = error_message
    result["Номер строки"] = excel_row

    errors.append(result)


def validate_input_file(input_file):
    """
    Проверяет существование входного файла,
    наличие необходимого листа и обязательных колонок.
    """
    if not os.path.exists(input_file):
        logger.error(
            "Файл не найден: %s",
            input_file,
        )
        raise FileNotFoundError(
            f"Файл не найден: {input_file}"
        )

    try:
        df = pd.read_excel(
            input_file,
            sheet_name="Заказы_сырье",
        )
    except ValueError as error:
        logger.error(
            "Лист 'Заказы_сырье' не найден"
        )
        raise ValueError(
            "Лист 'Заказы_сырье' не найден"
        ) from error

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
        logger.error(
            "В исходном файле отсутствуют обязательные колонки: %s",
            missing_columns,
        )
        raise ValueError(
            "В исходном файле отсутствуют обязательные колонки: "
            f"{', '.join(missing_columns)}"
        )

    return df


def process_file(
    input_file,
    output_file,
    telegram_bot_token=None,
    telegram_chat_id=None,
):
    """
    Обрабатывает Excel-файл и формирует итоговый отчёт.

    Функция проверяет входной файл, загружает исходные данные,
    находит дубликаты, нормализует строки, разделяет корректные
    и ошибочные записи, формирует отчёт по мастерам, сохраняет
    Excel-файл и отправляет Telegram-уведомление.
    """
    logger.info(
        "Обработка файла начата: %s",
        input_file,
    )

    # Проверяем входной файл и загружаем лист с заказами
    df = validate_input_file(input_file)

    logger.info(
        "Загружено строк: %s",
        len(df),
    )

    valid_rows = []
    errors = []

    # Находим все строки с повторяющимися ID
    # Все строки одного дублирующегося ID считаются ошибочными
    duplicate_indexes = set(find_duplicate_ids(df).index)

    logger.info(
        "Найдено строк с дублирующимися ID: %s",
        len(duplicate_indexes),
    )

    # Обрабатываем каждую строку исходного Excel-файла
    # Нумерация начинается с 2, потому что первая строка Excel содержит заголовки
    for excel_row, (index, row) in enumerate(
        df.iterrows(),
        start=2,
    ):
        # Дубликаты не передаём в нормализацию, а сразу добавляем в список ошибок
        if index in duplicate_indexes:
            add_error(errors, row.to_dict(), "Дубликат ID заказа", excel_row)
            continue

        # Обрабатываем и нормализуем текущую строку
        result, row_errors = process_row(row)

        if row_errors:
            add_error(
                errors,
                result,
                "; ".join(row_errors),
                excel_row,
            )
        else:
            valid_rows.append(result)

    logger.info(
        "Обработка завершена. Корректных строк: %s, "
        "ошибочных строк: %s",
        len(valid_rows),
        len(errors),
    )

    # Считаем количество каждого типа ошибки
    error_counter = Counter()

    for row in errors:
        error_message = row.get(
            "Причина ошибки",
            "",
        )

        if error_message:
            for error in error_message.split("; "):
                if error.strip():
                    error_counter[error.strip()] += 1

    for error, count in error_counter.items():
        logger.info(
            "Ошибка: %s — %s шт.",
            error,
            count,
        )

    # Формируем статистику по мастерам только из корректных строк
    report = build_report(valid_rows)

    logger.info(
        "Отчёт по мастерам сформирован. Мастеров: %s",
        len(report),
    )

    # Создаём итоговый Excel-файл
    create_report_file(report, errors, output_file)

    logger.info("Файл отчёта успешно создан: %s", output_file)

    # Отправляем Telegram-уведомление
    try:
        notify_telegram(
            telegram_bot_token,
            telegram_chat_id,
        )
        logger.info("Telegram-уведомление отправлено")
    except RuntimeError as error:
        logger.error("%s", error)
        raise

    return report, errors