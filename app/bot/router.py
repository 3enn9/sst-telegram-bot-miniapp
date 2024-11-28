from io import BytesIO
import aiofiles
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, WebAppInfo, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.engine import connection
from app.database.models import User
from app.database.orm_query import add_user, get_exports

router = Router(name=__name__)


@router.message(CommandStart())
@connection()
async def cmd_start(message: Message, session: AsyncSession, **kwargs):
    welcome_text = (
        "🚛 Добро пожаловать в бота bobcat64!\n\n"
        "📝 Здесь вы можете добавлять операции\n\n"
        "📈 Смотреть сколько операций вы выполнили за сегодня"
    )

    try:
        existing_user = await session.execute(select(User).filter(User.telegram_id == message.from_user.id))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user:
            print('сущетсвует')
        else:
            await add_user(session=session, telegram_id=message.from_user.id,
                           username=message.from_user.username,
                           first_name=message.from_user.first_name,
                           last_name=message.from_user.last_name, )

        def main_keyboard() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.button(text="📝 Добавить операцию", web_app=WebAppInfo(url=f"{settings.BASE_SITE}/{message.from_user.id}?username={message.from_user.username}"))
            kb.button(text="🚨 Добавить поломку", web_app=WebAppInfo(url=f"{settings.BASE_SITE}/breakdown/{message.from_user.id}?username={message.from_user.username}"))
            kb.button(text="💰 Касса(пока не работает)", web_app=WebAppInfo(url=f"{settings.BASE_SITE}/transactions/{message.from_user.id}?username={message.from_user.username}"))
            kb.button(text="📈 Операции за сегодня", callback_data="show_my_record")
            kb.adjust(1)
            return kb.as_markup()

        await message.answer(welcome_text, reply_markup=main_keyboard())

    except Exception as e:
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@router.callback_query(F.data == 'download_excel')
@connection()
async def send_excel(callback: CallbackQuery, session):
    try:
        # Получаем данные
        df = await get_exports(session=session)
        
        # Создаем временный файл
        temp_file_path = "temp_exports_data.xlsx"

        # Конвертируем DataFrame в Excel и сохраняем в буфер
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)  # Возвращаем указатель на начало буфера

        # Сохраняем данные из буфера в временный файл с помощью aiofiles
        async with aiofiles.open(temp_file_path, 'wb') as f:
            await f.write(buffer.getvalue())

        # Создаем объект InputFile из временного файла
        document = FSInputFile(temp_file_path, filename="exports_data.xlsx")
        
        # Отправляем файл в Telegram
        await callback.message.answer_document(document)
        await callback.answer()  # Закрыть уведомление

        # Удаляем временный файл после отправки
        await aiofiles.os.remove(temp_file_path)

    except Exception as e:
        print(f"Ошибка при отправке Excel: {e}")
        await callback.message.answer("Произошла ошибка при обработке вашего запроса. Попробуйте снова позже.")