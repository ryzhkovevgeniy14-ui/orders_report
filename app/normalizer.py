from datetime import datetime
import pandas as pd


# Допустимые статусы, которые уже находятся в нужном формате
VALID_STATUSES = {
    "Выполнен",
    "В работе",
    "Отменен",
    "Перенесен",
    "Новый",
}

# Известные варианты написания статусов и соответствующие им нормализованные значения
STATUS_MAP = {
    "ОТМЕНА": "Отменен",
    "Закрыт": "Выполнен",
    "Отказ клиента": "Отменен",
    "выполнен": "Выполнен",
}

# Ошибочные значения статуса
INVALID_STATUSES = {
    "Завершено?",
    "Готово",
}

# Известные варианты написания городов и соответствующие им правильные названия
CITY_ALIASES = {
    "новоросийск": "Новороссийск",
    "анапа": "Анапа",
    "ростов на дону": "Ростов-на-Дону",
    "краснадар": "Краснодар",
}

# Значения, соответствующие "Да" для полей типа Да/Нет
RECLAMATION_TRUE = {
    "да",
    "yes",
    "1",
}

# Значения, соответствующие "Нет" для полей типа Да/Нет
RECLAMATION_FALSE = {
    "нет",
    "no",
    "0",
}

# Для поля "Фото загружено" используются варианты как для рекламации
PHOTO_TRUE = RECLAMATION_TRUE
PHOTO_FALSE = RECLAMATION_FALSE


# Нормализация статусов
def normalize_status(value):
    """
    Нормализует статус заказа.
    """
    # Проверяем пустое или некорректное значение
    if not isinstance(value, str):
        return None, "Неоднозначный статус"

    # Убираем пробелы по краям строки
    status = value.strip()

    # Если статус уже соответствует допустимому формату, возвращаем его без изменений
    if status in VALID_STATUSES:
        return status, None

    # Проверяем известные альтернативные варианты написания
    if status in STATUS_MAP:
        return STATUS_MAP[status], None

    # Проверяем ошибочные значения
    if status in INVALID_STATUSES:
        return None, "Неоднозначный статус"

    return None, "Неизвестный статус"


# Нормализация дат
def normalize_russian_date(value):
    """
    Преобразует русское название месяца мая в числовой формат.

    Поддерживаются варианты с "мая" и "май".
    """
    # Если значение не является строкой, возвращаем его без изменений
    if not isinstance(value, str):
        return value

    value = value.lower().strip()

    # "27 мая 2026" -> "27.05.2026"
    if "мая" in value:
        parts = value.split()

        day = parts[0]
        year = parts[2]

        return f"{day}.05.{year}"

    # "май 15 2026" -> "15.05.2026"
    if "май" in value:
        parts = value.split()

        day = parts[1]
        year = parts[2]

        return f"{day}.05.{year}"

    return value


def normalize_date(value):
    """
    Приводит дату к единому формату YYYY-MM-DD.
    """
    # Пустая дата считается некорректной
    if pd.isna(value):
        return None, "Некорректная дата"

    # Приводим дату к строковому представлению
    value = str(value)

    # Сначала обрабатываем даты с русским названием месяца
    value = normalize_russian_date(value)

    # Перебираем поддерживаемые форматы входных данных
    formats = [
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
    ]

    for date_format in formats:
        try:
            date = datetime.strptime(value, date_format)

            return date.strftime("%Y-%m-%d"), None

        except ValueError:
            continue

    return None, "Некорректная дата"


# Нормализация сумм
def normalize_amount(value):
    """
    Приводит сумму заказа к числовому формату.

    Поддерживаются числа, строки с рублями, пробелами
    и десятичной запятой.
    """
    # Пустая ячейка Excel
    if pd.isna(value):
        return None, "Пустая сумма"

    # Если значение уже является числом, проверяем только его знак
    if isinstance(value, (int, float)):
        if value < 0:
            return None, "Отрицательная сумма"

        return float(value), None

    value = str(value).strip()

    # Известные значения, которые нельзя преобразовать в число
    if value in {"не указано", "abc", "три тысячи"}:
        return None, "Некорректная сумма"

    # Отрицательные значения считаем ошибочными
    if value.startswith("-"):
        return None, "Отрицательная сумма"

    # Убираем обозначения валюты и пробелы
    value = value.replace("₽", "")
    value = value.replace("руб.", "")
    value = value.replace(" ", "")

    # Меняем запятую на точку
    value = value.replace(",", ".")

    try:
        amount = float(value)

        return amount, None

    except ValueError:
        return None, "Некорректная сумма"


# Нормализация мастера
def normalize_master(value):
    """
    Нормализует ФИО мастера.

    Убирает лишние пробелы и приводит каждое слово
    к формату с заглавной первой буквой.
    """
    # Пустое значение
    if pd.isna(value):
        return None, "Пустой мастер"

    # Приводим к строке и убираем края
    value = str(value).strip()

    # Убираем лишние пробелы между словами
    value = " ".join(value.split())

    # Приводим каждое слово к виду "Имя Фамилия"
    value = " ".join(word.capitalize() for word in value.split())

    return value, None


def normalize_city(value):
    """
    Нормализует название города.

    Исправляет известные опечатки и приводит название
    к согласованному написанию.
    """
    # Пустое значение
    if pd.isna(value):
        return None, "Пустой город"

    # Приводим к строке и убираем пробелы по краям
    value = str(value).strip()

    # Убираем лишние пробелы внутри
    value = " ".join(value.split())

    # Используем нижний регистр только для поиска в словаре
    city_key = value.lower()

    # Исправляем известные ошибки
    if city_key in CITY_ALIASES:
        return CITY_ALIASES[city_key], None

    # Если название города уже корректно
    return value, None


def normalize_reclamation(value):
    """
    Приводит значение рекламации к "Да" или "Нет".
    """
    # Пустое значение
    if pd.isna(value):
        return None, "Пустая рекламация"

    value = str(value).strip().lower()

    if value in RECLAMATION_TRUE:
        return "Да", None

    if value in RECLAMATION_FALSE:
        return "Нет", None

    return None, "Неизвестное значение рекламации"


def normalize_photo(value):
    """
    Приводит значение наличия фотографии к "Да" или "Нет".
    """
    # Проверяем пустое значение
    if pd.isna(value):
        return None, "Пустое значение фото"

    value = str(value).strip().lower()

    if value in PHOTO_TRUE:
        return "Да", None

    if value in PHOTO_FALSE:
        return "Нет", None

    return None, "Неизвестное значение фото"