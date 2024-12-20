from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import BigInteger, Float, ForeignKey, Integer, TIMESTAMP, func, String
from typing import Optional


class Base(DeclarativeBase):
    __abstract__ = True  # Абстрактный базовый класс, чтобы избежать создания отдельной таблицы

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    balance: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    exports = relationship("Export", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Firm(Base):
    __tablename__ = 'firms'

    name: Mapped[Optional[str]] = mapped_column(String, nullable=False)
    # Связь с адресами фирмы (множество адресов)
    addresses = relationship("Address", back_populates="firm")

    # Связь с экспортами
    exports = relationship("Export", back_populates="firm")


class Address(Base):
    __tablename__ = 'addresses'

    firm_id: Mapped[int] = mapped_column(ForeignKey('firms.id'), nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)

    # Связь с фирмой
    firm = relationship("Firm", back_populates="addresses")

    # Связь с экспортами
    exports = relationship("Export", back_populates="address")


class Export(Base):
    __tablename__ = 'exports'

    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    firm_id: Mapped[int] = mapped_column(ForeignKey('firms.id'), nullable=False)
    address_id: Mapped[int] = mapped_column(ForeignKey('addresses.id'), nullable=False)

    numb_tank_taken: Mapped[Optional[str]] = mapped_column(String)
    numb_tank_drop: Mapped[Optional[str]] = mapped_column(String)
    dump_name: Mapped[Optional[str]] = mapped_column(String)

    # Связь с моделью User
    user = relationship("User", back_populates="exports")

    # Связь с моделью Firm
    firm = relationship("Firm", back_populates="exports")

    # Связь с моделью Address
    address = relationship("Address", back_populates="exports")

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'), nullable=False)  # Ссылка на пользователя
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Сумма транзакции (приход или расход)
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)  # Тип операции: "income" или "expense"
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Описание транзакции

    user = relationship("User", back_populates="transactions")
