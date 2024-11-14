from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User, Firm


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


async def get_all_firms(session: AsyncSession):
    result = await session.execute(select(Firm))

    # Извлекаем все результаты
    firms = result.scalars().all()

    return firms


async def get_addresses_by_firm_name(session: AsyncSession, firm_name: str):
    # Выполним запрос, чтобы найти фирму по названию и получить связанные с ней адреса
    result = await session.execute(
        select(Firm).filter(Firm.name == firm_name).options(
            selectinload(Firm.addresses)  # Загрузим связанные адреса
        )
    )

    firm = result.scalar_one_or_none()  # Получаем единственную фирму

    if firm:
        # Если фирма найдена, возвращаем ее адреса
        return [address.address for address in firm.addresses]
    return []  # Если фирма не найдена, возвращаем пустой список