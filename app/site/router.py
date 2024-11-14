import os
import shutil
from io import BytesIO
from typing import Optional

from aiogram.types import InputFile, BufferedInputFile
from fastapi import APIRouter, Form, Query, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from starlette.responses import RedirectResponse

from app.bot.create_bot import bot

router = APIRouter(prefix='', tags=['САЙТ'])
templates = Jinja2Templates(directory='app/templates')

# Пример списка фирм
firms_db = [
    "ООО Рога и Копыта",
    "ЗАО Фирма-1",
    "ИП Бобров",
    "Компания АБС",
    "Магазин Плюс",
    "ООО СарстройТех"
]

# Путь для сохранения файлов
UPLOAD_DIRECTORY = "uploads/"

# Убедитесь, что директория существует
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@router.get("/search_firm")
async def search_firm(query: str = Query(...)):
    # Проверка, что query не пустой
    # Фильтруем список firms_db по введённой части имени
    filtered_firms = [firm for firm in firms_db if query.lower() in firm.lower()]

    # Возвращаем JSON-ответ с отфильтрованным списком
    return JSONResponse(content=filtered_firms)


# Пример обработки запроса через FastAPI для рендеринга HTML
@router.get("/{user_id}", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int):
    return templates.TemplateResponse("index.html", {"request": request, "user_id": user_id})


# Обработка отправленных данных
@router.post("/{user_id}/submit", response_class=HTMLResponse)
async def submit_form(
        request: Request,
        search: str = Form(...),
        address: str = Form(...),
        action: str = Form(...),
        taken_basket_number: str = Form(...),
        placed_basket_number: str = Form(...),
        choice: str = Form(...),
        weight: Optional[str] = Form(None),
        photo: Optional[UploadFile] = File(...)  # Ожидаем файл
):
    # Обработка значения поля weight
    weight_value = float(weight) if weight and weight.strip() else 'Не указан'

    # Извлекаем user_id из параметров пути
    user_id = request.path_params['user_id']

    # Получение данных из формы
    content = (f"Фирма: {search}\n"
                 f"Адрес: {address}\n"
                 f"Действие: {action}\nНомер взятого б.: {taken_basket_number}\n"
                 f"Номер поставленного б.: {placed_basket_number}\n"
                 f"Свалка: {choice}\nВес: {weight_value}\n"
                 f"user_id: {user_id}")

    if photo:
        try:
            # Читаем содержимое файла в память
            photo_bytes = await photo.read()

            # Создаем объект BufferedInputFile из байтов
            input_photo = BufferedInputFile(photo_bytes, filename=photo.filename)

            # Отправляем фото в Telegram
            await bot.send_photo(chat_id="877804669", photo=input_photo, caption=content)
            saved_photo = f'Фото отправлено: {photo.filename}'
        except Exception as e:
            saved_photo = f'Ошибка при отправке фото: {str(e)}'
    else:
        saved_photo = 'Не загружено'

    return RedirectResponse(url=request.url_for('submit_form', user_id=user_id), status_code=303)
