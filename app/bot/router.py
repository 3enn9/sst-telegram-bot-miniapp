from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.engine import connection
from app.database.models import User
from app.database.orm_query import add_user

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
            kb.button(text="📝 Добавить операцию", web_app=WebAppInfo(url=f"{settings.BASE_SITE}/{message.from_user.id}"))
            # kb.button(text="🏆 Лидеры 2048", web_app=WebAppInfo(url=f"{settings.BASE_SITE}/records"))
            kb.button(text="📈 Операции за сегодня", callback_data="show_my_record")
            kb.adjust(1)
            return kb.as_markup()

        await message.answer(welcome_text, reply_markup=main_keyboard())

    except Exception as e:
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")
