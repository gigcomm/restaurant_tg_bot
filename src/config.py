from sqlalchemy import BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import ForeignKey

import tracemalloc

tracemalloc.start()

user = 'postgres'
password = '1'
host = 'localhost'
port = '5432'
db_name = 'db_kurs'
# Создайте движок для подключения к базе данных
engine = create_async_engine(f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}', echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass



class Food_groups(Base):
    __tablename__ = 'food_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str] = mapped_column()

    menu = relationship('Menu', back_populates='food_groups')

class Menu(Base):
    __tablename__ = 'menu'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column()
    pic: Mapped[str] = mapped_column()
    fk_menu_group: Mapped[int] = mapped_column(ForeignKey('food_groups.id'))

    food_groups = relationship('Food_groups', back_populates='menu')
    orders = relationship('Orders', secondary="orders_menu")
    restaurant = relationship('Restaurant', back_populates='menu')



class Status(Base):
    __tablename__ = 'status'
    id: Mapped[int] = mapped_column(primary_key=True)
    status_name: Mapped[str] = mapped_column()

    orders = relationship('Orders', back_populates='status')

class Orders(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_adress: Mapped[str] = mapped_column()
    order_date: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    status_id: Mapped[int] = mapped_column(ForeignKey('status.id'))

    status = relationship('Status', back_populates='orders')
    client = relationship('Client', back_populates='orders')
    menu = relationship("Menu", secondary='orders_menu')


class Client(Base):
    __tablename__ = 'client'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    adress: Mapped[str] = mapped_column()
    fk_client_order: Mapped[int] = mapped_column(ForeignKey('orders.id'))

    orders = relationship('Orders', back_populates='client')
    restaurant = relationship('Restaurant', back_populates='client')


class Ad_cods(Base):
    __tablename__ = 'ad_cods'
    id: Mapped[int] = mapped_column(primary_key=True)
    adm_password: Mapped[str] = mapped_column()
    tg_id = mapped_column(BigInteger)

    restaurant = relationship('Restaurant', back_populates='ad_cods')


class Orders_menu(Base):
    __tablename__ = 'orders_menu'
    fk_fk_order: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    fk_fk_menu: Mapped[int] = mapped_column(ForeignKey('menu.id'), primary_key=True)
    count_in_menu: Mapped[int] = mapped_column()


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    adress: Mapped[str] = mapped_column()
    fk_restaurant_menu: Mapped[int] = mapped_column(ForeignKey('menu.id'))
    fk_restaurant_client: Mapped[int] = mapped_column(ForeignKey('client.id'))
    fk_restaurant_adcods: Mapped[int] = mapped_column(ForeignKey('ad_cods.id'))

    ad_cods = relationship('Ad_cods', back_populates='restaurant')
    client = relationship('Client', back_populates='restaurant')
    menu = relationship('Menu', back_populates='restaurant')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
