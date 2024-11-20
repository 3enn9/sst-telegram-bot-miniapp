from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Address, Export, User, Firm


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

async def add_export(
    session: AsyncSession,
    telegram_id: int,
    firm_id: int,
    address_id: int,
    numb_tank_taken: Optional[str] = None,
    numb_tank_drop: Optional[str] = None,
    dump_name: Optional[str] = None
):
    try:
        # Создаем объект Export
        new_export = Export(
            telegram_id=telegram_id,
            firm_id=firm_id,
            address_id=address_id,
            numb_tank_taken=numb_tank_taken,
            numb_tank_drop=numb_tank_drop,
            dump_name=dump_name
        )

        # Добавляем его в сессию
        session.add(new_export)

        # Коммитим изменения в базе данных
        await session.commit()

        return new_export

    except IntegrityError as e:
        # Обработка ошибки уникальности или других нарушений
        await session.rollback()
        raise Exception(f"Ошибка добавления записи: {str(e)}")
    

async def get_firm_id_by_name(session: AsyncSession, firm_name: str):
    # Выполняем запрос для поиска фирмы по имени
    result = await session.execute(select(Firm.id).filter(Firm.name == firm_name))
    
    # Получаем результат (если фирма найдена, возвращаем ее id)
    firm_id = result.scalars().first()
    
    if firm_id:
        return firm_id
    else:
        return None  # Возвращаем None, если фирма с таким именем не найдена

from sqlalchemy.future import select

async def get_address_id_by_name(session: AsyncSession, address_name: str):
    # Выполняем запрос для поиска адреса по имени
    result = await session.execute(select(Address.id).filter(Address.name == address_name))
    
    # Получаем результат (если адрес найден, возвращаем его id)
    address_id = result.scalars().first()
    
    if address_id:
        return address_id
    else:
        return None  # Возвращаем None, если адрес с таким именем не найден


async def add_firm(session: AsyncSession, firm_name: str):
    # Создаем новый объект фирмы
    new_firm = Firm(name=firm_name)

    try:
        # Добавляем объект фирмы в сессию
        session.add(new_firm)
        # Подтверждаем изменения
        await session.commit()

        # Получаем id добавленной фирмы
        return new_firm.id
    except IntegrityError:
        # Обработка ошибки, если фирма с таким именем уже существует
        await session.rollback()
        print(f"Фирма с именем '{firm_name}' уже существует.")
        return None  # Можно вернуть None или какое-то другое значение в случае ошибки
    except Exception as e:
        # Обработка других ошибок
        await session.rollback()
        print(f"Произошла ошибка: {e}")
        return None
    

async def add_address(session: AsyncSession, address_name: str, firm_id) -> int:
    # Создаем новый объект адреса
    new_address = Address(address=address_name, firm_id=firm_id)

    try:
        # Добавляем объект адреса в сессию
        session.add(new_address)
        # Подтверждаем изменения
        await session.commit()
        
        # Получаем id добавленного адреса
        return new_address.id
    except IntegrityError:
        # Обработка ошибки, если адрес с таким именем уже существует
        await session.rollback()
        print(f"Адрес '{address_name}' уже существует.")
        return None  # Можно вернуть None или какое-то другое значение в случае ошибки
    except Exception as e:
        # Обработка других ошибок
        await session.rollback()
        print(f"Произошла ошибка: {e}")
        return None