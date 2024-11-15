import logging
from typing import Optional

from aiogram.types import InputFile, BufferedInputFile
from fastapi import APIRouter, Form, Query, HTTPException, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.bot.create_bot import bot
from app.database.engine import connection, get_session
from app.database.orm_query import get_all_firms, get_addresses_by_firm_name

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

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат логов
)


@router.get("/search_firm")
async def search_firm(query: str = Query(...), session: AsyncSession = Depends(get_session)):
    firms = await get_all_firms(session)
    filtered_firms = [firm.name for firm in firms if query.lower() in firm.name.lower()]
    # Возвращаем JSON-ответ с отфильтрованным списком
    return JSONResponse(content=filtered_firms)


@router.get("/search_address")
async def search_address(query: str = Query(...), firm: str = Query(...), session: AsyncSession = Depends(get_session)):
    # Логика поиска по адресу и названию фирмы
    addresses = await get_addresses_by_firm_name(session, firm)
    return JSONResponse(content=addresses)


# Пример обработки запроса через FastAPI для рендеринга HTML
@router.get("/{user_id}", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int, message: str = ''):
    return templates.TemplateResponse("index.html", {"request": request, "user_id": user_id, "message": message})


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
               f"Действие: {action}\n"
               f"Взял: {taken_basket_number}\n"
               f"Поставил: {placed_basket_number}\n"
               f"Свалка: {choice}\n"
               f"Вес: {weight_value}\n"
               f"user_id: {user_id}")

    # Выполните логику отправки данных и фото
    success_message = None  # Сообщение об успехе

    if photo:
        try:
            # Читаем содержимое файла в память
            photo_bytes = await photo.read()

            # Создаем объект BufferedInputFile из байтов
            input_photo = BufferedInputFile(photo_bytes, filename=photo.filename)

            # Отправляем фото в Telegram
            await bot.send_photo(chat_id=settings.CHAT_ID, photo=input_photo, caption=content)
            success_message = "Фото и данные успешно отправлены!"
            logging.info(success_message)  # Логируем сообщение об успехе
        except Exception as e:
            logging.error(f'Ошибка при отправке фото: {str(e)}')  # Логируем сообщение об ошибке
    else:
        logging.warning('Не загружено')

    # Сохраняем сообщение в сессии или передавайте параметр в URL (например, через Query String)
    redirect_url = f"/{user_id}?message={success_message}"
    return RedirectResponse(redirect_url, status_code=303)