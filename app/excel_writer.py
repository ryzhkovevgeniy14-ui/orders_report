from openpyxl import Workbook
from openpyxl.styles import Font


def create_report_file(report, errors, filename="report.xlsx"):
    """
    Создаёт итоговый Excel-файл с отчётом по мастерам
    и отдельным листом с ошибочными строками.

    На листе "Отчёт" сохраняется статистика по мастерам.
    На листе "Ошибки" сохраняются исходные данные строк,
    в которых были обнаружены ошибки.
    """
    # Создаём новую книгу Excel
    workbook = Workbook()

    # Получаем первый лист и переименовываем его
    report_sheet = workbook.active
    report_sheet.title = "Отчёт"

    # Заголовки основного отчёта
    report_headers = [
        "Мастер",
        "Количество выполненных заказов",
        "Сумма выполненных заказов",
        "Количество рекламаций",
        "Процент рекламаций",
        "Количество заказов без фото",
        "Количество отмененных заказов",
    ]

    report_sheet.append(report_headers)

    # Заполняем отчёт данными по каждому мастеру
    for row in report:
        report_sheet.append([
            row["Мастер"],
            row["Количество выполненных заказов"],
            row["Сумма выполненных заказов"],
            row["Количество рекламаций"],
            row["Процент рекламаций"],
            row["Количество заказов без фото"],
            row["Количество отмененных заказов"],
        ])

    # Делаем заголовки таблицы жирными
    for cell in report_sheet[1]:
        cell.font = Font(bold=True)

    # Форматируем суммы как денежные значения
    for cell in report_sheet["C"][1:]:
        cell.number_format = '#,##0.00 "₽"'

    # Форматируем процент рекламаций
    for cell in report_sheet["E"][1:]:
        cell.number_format = "0.00%"

    # Добавляем автофильтр ко всей таблице
    report_sheet.auto_filter.ref = report_sheet.dimensions

    # Закрепляем строку с заголовками при прокрутке
    report_sheet.freeze_panes = "A2"

    # Устанавливаем ширину колонок основного отчёта
    column_widths = {
        "A": 20,
        "B": 35,
        "C": 31,
        "D": 26,
        "E": 24,
        "F": 30,
        "G": 34,
    }

    for column, width in column_widths.items():
        report_sheet.column_dimensions[column].width = width

    # Создаём отдельный лист для ошибочных строк
    errors_sheet = workbook.create_sheet("Ошибки")

    # Заполняем лист только если ошибки действительно найдены
    if errors:
        # Берём названия колонок из первой ошибочной строки
        error_headers = list(errors[0].keys())
        errors_sheet.append(error_headers)

        # Добавляем все ошибочные строки
        for row in errors:
            errors_sheet.append([
                row.get(header)
                for header in error_headers
            ])

        # Делаем заголовки таблицы жирными
        for cell in errors_sheet[1]:
            cell.font = Font(bold=True)

        # Добавляем автофильтр
        errors_sheet.auto_filter.ref = errors_sheet.dimensions

        # Закрепляем строку с заголовками
        errors_sheet.freeze_panes = "A2"

        # Устанавливаем ширину колонок
        error_widths = {
            "A": 18,
            "B": 16,
            "C": 18,
            "D": 22,
            "E": 20,
            "F": 15,
            "G": 20,
            "H": 35,
            "I": 18,
        }

        for column, width in error_widths.items():
            errors_sheet.column_dimensions[column].width = width

    # Сохраняем готовый Excel-файл
    workbook.save(filename)