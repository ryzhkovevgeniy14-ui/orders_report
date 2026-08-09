from app import normalizer


def process_row(row):
    """
    Нормализует и проверяет одну строку исходных данных.

    Для каждого поля вызывается соответствующая функция
    нормализации. Если значение некорректно, в результат
    сохраняется исходное значение, а ошибка добавляется
    в список ошибок строки.
    """
    errors = []
    result = {}

    # Нормализуем статус заказа
    original_value = row["Статус заказа"]
    value, error = normalizer.normalize_status(original_value)

    result["Статус заказа"] = original_value if error else value

    if error:
        errors.append(error)

    # Нормализуем дату заказа
    original_value = row["Дата"]
    value, error = normalizer.normalize_date(original_value)

    result["Дата"] = original_value if error else value

    if error:
        errors.append(error)

    # Нормализуем сумму заказа
    original_value = row["Сумма"]
    value, error = normalizer.normalize_amount(original_value)

    result["Сумма"] = original_value if error else value

    if error:
        errors.append(error)

    # Нормализуем ФИО мастера
    original_value = row["Мастер"]
    value, error = normalizer.normalize_master(original_value)

    result["Мастер"] = original_value if error else value

    if error:
        errors.append(error)

    # Нормализуем название города
    original_value = row["Город"]
    value, error = normalizer.normalize_city(original_value)

    result["Город"] = original_value if error else value

    if error:
        errors.append(error)

    # Нормализуем значение рекламации
    original_value = row["Рекламация"]
    value, error = normalizer.normalize_reclamation(original_value)

    result["Рекламация"] = original_value if error else value

    if error:
        errors.append(error)

    # Нормализуем наличие фотографии
    original_value = row["Фото загружено"]
    value, error = normalizer.normalize_photo(original_value)

    result["Фото загружено"] = original_value if error else value

    if error:
        errors.append(error)

    return result, errors