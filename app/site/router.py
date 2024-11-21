import logging
from typing import Optional

from aiogram.types import InputFile, BufferedInputFile
from fastapi import APIRouter, Form, Query, HTTPException, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Response
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.bot.create_bot import bot
from app.database.engine import connection, get_session
from app.database.orm_query import add_address, add_export, add_firm, get_address_id_by_name, get_all_firms, get_addresses_by_firm_name, get_firm_id_by_name

router = APIRouter(prefix='', tags=['САЙТ'])
templates = Jinja2Templates(directory='app/templates')


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат логов
)


@router.get("/search_firm")
async def search_firm(query: str = Query(...), session: AsyncSession = Depends(get_session)):
    firms = await get_all_firms(session)
    filtered_firms = [firm.name for firm in firms if query.lower() in firm.name.lower()]
    filtered_firms.append('микс')
    # Возвращаем JSON-ответ с отфильтрованным списком
    return JSONResponse(content=filtered_firms)


@router.get("/search_address")
async def search_address(query: str = Query(...), firm: str = Query(...), session: AsyncSession = Depends(get_session)):
    # Логика поиска по адресу и названию фирмы
    addresses = await get_addresses_by_firm_name(session, firm)
    return JSONResponse(content=addresses)


# Пример обработки запроса через FastAPI для рендеринга HTML
@router.get("/{user_id}", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int, message: str = '',  username: str = Query(None)):
    return templates.TemplateResponse("index.html", {"request": request, "user_id": user_id, "message": message,  "username": username})


@router.get("/breakdown/{user_id}")
async def add_breakdown(request: Request, user_id: int, username: str = Query(None), response: Response = None):
    response.headers["Cache-Control"] = "no-store"
    return templates.TemplateResponse("breakdown.html", {"request": request, "user_id": user_id, "username": username})


# Обработка отправленных данных
@router.post("/{user_id}/submit", response_class=HTMLResponse)
async def submit_form(
        request: Request,
        search: str = Form(...),
        address: str = Form(...),
        action: str = Form(...),
        taken_basket_number: str = Form(None),
        placed_basket_number: str = Form(None),
        choice: str = Form(...),
        weight: Optional[str] = Form(None),
        username: str = Query(None),
        photo: Optional[UploadFile] = File(None), 
        session: AsyncSession = Depends(get_session)
):
    # Обработка значения поля weight
    weight_value = float(weight) if weight and weight.strip() else 'Не указан'

    addresses = await get_addresses_by_firm_name(session, search)
    firm_id = await get_firm_id_by_name(session, search)
    firm_id = firm_id or await add_firm(session, search)

    # Извлекаем user_id из параметров пути
    user_id = int(request.path_params['user_id'])

    # Получение данных из формы
    content = (f"Фирма: <b>{search}</b>\n"
               f"Адрес: <b>{address}</b>\n"
               f"Действие: <b>{action}</b>\n"
               f"Взял: <b>{taken_basket_number}</b>\n"
               f"Поставил: <b>{placed_basket_number}</b>\n"
               f"Свалка: <b>{choice}</b>\n"
               f"Вес: <b>{weight_value}</b>\n"
               f"Водитель: <b>@{username}</b>")

 # Инициализация address_id с None или с каким-либо значением по умолчанию
    address_id = None

    if address not in addresses:
        address_id = await add_address(session, address, firm_id)
    else:
        # Если адрес уже существует, получить его ID
        address_id = await get_address_id_by_name(session, address)

    # Выполните логику отправки данных и фото
    success_message = None  # Сообщение об успехе
    await add_export(session = session,
                      telegram_id = user_id,
                      firm_id = firm_id,
                      address_id = address_id,
                      numb_tank_taken = taken_basket_number or None,
                      numb_tank_drop = placed_basket_number or None,
                      dump_name = choice or None)
    
    success_message = "Данные успешно отправлены!"

    if photo and photo.filename and photo.size > 0:
        try:
            # Читаем содержимое файла в память
            photo_bytes = await photo.read()

            # Создаем объект BufferedInputFile из байтов
            input_photo = BufferedInputFile(photo_bytes, filename=photo.filename)

            # Отправляем фото в Telegram
            await bot.send_photo(chat_id=settings.CHAT_ID, photo=input_photo, caption=content, parse_mode="HTML")
            
            logging.info(success_message)  # Логируем сообщение об успехе
        except Exception as e:
            logging.error(f'Ошибка при отправке фото: {str(e)}')  # Логируем сообщение об ошибке
    else:
        # Отправляем фото в Telegram
            await bot.send_message(chat_id=settings.CHAT_ID, text=content, parse_mode="HTML")
            logging.info(success_message)  # Логируем сообщение об успехе

    # Сохраняем сообщение в сессии или передавайте параметр в URL (например, через Query String)
    redirect_url = f"/{user_id}?message={success_message}&username={username}"
    return RedirectResponse(redirect_url, status_code=303)