from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from app.service import process_file


def main():
    """
    Запускает обработку исходного Excel-файла.
    """
    try:
        process_file(
            input_file="input_data/Тестовое_задание.xlsx",
            output_file="report.xlsx",
            telegram_bot_token=TELEGRAM_BOT_TOKEN,
            telegram_chat_id=TELEGRAM_CHAT_ID,
        )
        print("✅ Обработка завершена успешно")
    except RuntimeError as error:
        print(f"❌ Ошибка: {error}")


if __name__ == "__main__":
    main()