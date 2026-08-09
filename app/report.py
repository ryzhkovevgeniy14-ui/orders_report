def calculate_master_statistics(rows):
    """
    Рассчитывает статистику по заказам одного мастера.

    Учитываются количество и сумма выполненных заказов,
    количество рекламаций, заказов без фотографии
    и отменённых заказов.
    """
    completed_count = 0
    completed_sum = 0
    reclamation_count = 0
    without_photo_count = 0
    cancelled_count = 0

    # Анализируем все корректные заказы мастера
    for row in rows:
        # Считаем выполненные заказы и их общую сумму
        if row["Статус заказа"] == "Выполнен":
            completed_count += 1
            completed_sum += row["Сумма"]

            # Считаем количество рекламаций
            if row["Рекламация"] == "Да":
                reclamation_count += 1

        # Считаем заказы, для которых не загружено фото
        if row["Фото загружено"] == "Нет":
            without_photo_count += 1

        # Считаем отменённые заказы
        if row["Статус заказа"] == "Отменен":
            cancelled_count += 1

    # Рассчитываем процент рекламаций относительно выполненных заказов
    if completed_count > 0:
        reclamation_percent = reclamation_count / completed_count
    else:
        reclamation_percent = 0

    return {
        "Количество выполненных заказов": completed_count,
        "Сумма выполненных заказов": completed_sum,
        "Количество рекламаций": reclamation_count,
        "Процент рекламаций": reclamation_percent,
        "Количество заказов без фото": without_photo_count,
        "Количество отмененных заказов": cancelled_count,
    }


def build_report(valid_rows):
    """
    Формирует итоговый отчёт, группируя корректные заказы по мастерам.

    Для каждого мастера рассчитывается отдельная статистика.
    """
    masters = {}

    # Группируем заказы по мастерам
    for row in valid_rows:
        master = row["Мастер"]

        if master not in masters:
            masters[master] = []

        masters[master].append(row)

    report = []

    # Рассчитываем статистику для каждого мастера
    for master, rows in masters.items():
        statistics = calculate_master_statistics(rows)

        result = {
            "Мастер": master,
            **statistics,
        }

        report.append(result)

    return report