from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


async def add_user(session: AsyncSession, telegram_id: int, username: Optional[str] = None,
                   first_name: Optional[str] = None, last_name: Optional[str] = None) -> User:
    # Проверяем, существует ли пользователь с таким telegram_id
    existing_user = await session.execute(select(User).filter(User.telegram_id == telegram_id))
    existing_user = existing_user.scalar_one_or_none()

    if existing_user:
        raise ValueError("Пользователь с таким telegram_id уже существует.")

    # Создаем нового пользователя
    new_user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )

    # Добавляем пользователя в сессию
    session.add(new_user)

    # Коммитим изменения в базе данных
    await session.commit()

    # Возвращаем добавленного пользователя
    return new_user
