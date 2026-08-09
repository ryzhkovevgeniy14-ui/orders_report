import os
import shutil
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from app.logger import setup_logger
from app.service import process_file


logger = setup_logger()

app = FastAPI(
    title="Автоматизация отчёта по заказам",
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Раздаём HTML, CSS и JavaScript из папки frontend
app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend",
)


@app.get("/")
def index():
    """
    Возвращает главную страницу веб-интерфейса.
    """
    return FileResponse("frontend/index.html")


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """
    Принимает Excel-файл, обрабатывает его
    и возвращает готовый отчёт.
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Файл не выбран.",
        )

    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Пожалуйста, загрузите Excel-файл.",
        )

    input_path = os.path.join(
        UPLOAD_DIR,
        file.filename,
    )

    output_filename = (
        f"report_{uuid.uuid4().hex[:8]}.xlsx"
    )
    output_path = os.path.join(
        OUTPUT_DIR,
        output_filename,
    )

    try:
        # Сохраняем загруженный файл
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Обрабатываем файл
        process_file(
            input_file=input_path,
            output_file=output_path,
            telegram_bot_token=TELEGRAM_BOT_TOKEN,
            telegram_chat_id=TELEGRAM_CHAT_ID,
        )

        # Проверяем, что отчёт создан
        if not os.path.exists(output_path):
            raise HTTPException(
                status_code=500,
                detail="Файл отчёта не был создан.",
            )

        return FileResponse(
            path=output_path,
            filename="report.xlsx",
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        # Telegram ошибка
        logger.error("Ошибка Telegram: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Не удалось отправить Telegram-уведомление.",
        ) from error

    except HTTPException:
        raise

    except Exception as error:
        logger.error("Ошибка обработки: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Ошибка при обработке файла.",
        ) from error

    finally:
        # Удаляем исходный загруженный файл
        if os.path.exists(input_path):
            os.remove(input_path)

        file.file.close()