from src.config import *
from src.config import async_session
from sqlalchemy import select, update, delete, insert, func


async def getall_food_group():  # Все группы блюд
    async with async_session() as session:
        result = await session.scalars(select(Food_groups))
        session.close()

    return result


async def getall_orders():  # Все заказы
    async with async_session() as session:
        result = await session.scalars(select(Orders))
        session.close()
    return result


async def get_ad_cods():  # Выбрать все записи из ад_кодс
    async with async_session() as session:
        result = await session.scalars(select(Ad_cods))
        await session.close()

    return result


async def getall_client():  # Все клиенты
    async with async_session() as session:
        result = await session.scalars(select(Client))
        session.close()

    return result


async def getall_menu(group):  # Все позиции меню
    async with async_session() as session:
        result = await session.scalars(
            select(Menu).join(Food_groups, Menu.fk_menu_group == Food_groups.id).where(Food_groups.group_name == group))
        await session.close()

    return result


async def getall_orders_menu():  # Все связи многие ко многим
    async with async_session() as session:
        result = await session.scalars(select(Orders_menu))
        session.close()

    return result


async def getall_restaurant():  # Все рестораны
    async with async_session() as session:
        result = await session.scalars(select(Restaurant))
        session.close()

    return result


async def getall_status():  # Все статусы (оплачен, не оплачен и тд)
    async with async_session() as session:
        result = await session.scalars(select(Status))
        session.close()

    return result


async def menu_delete(name_str):  # Удаляет позицию меню по названию блюда
    async with async_session() as session:
        session.execute(delete(Menu).where(Menu.name == name_str))
        session.commit()
        session.close()


async def menu_upd_price(name_str, new_price):  # Обновляем цену по названию блюда
    async with async_session() as session:
        await session.execute(update(Menu).where(Menu.name == name_str).values(price=new_price))
        session.commit()
        session.close()


async def menu_upd_name(name_str, new_name):  # Обновляет название блюда по названию блюда
    async with async_session() as session:
        await session.execute(update(Menu).where(Menu.name == name_str).values(name=new_name))
        session.commit()
        session.close()


async def menu_upd_description(name_str, new_desc):  # Обновляет описание блюда по названию
    async with async_session() as session:
        await session.execute(update(Menu).where(Menu.name == name_str).values(description=new_desc))
        session.commit()
        session.close()


async def menu_upd_pic(name_str, new_pic):  # Обновляем фотку по названию блюда
    async with async_session() as session:
        await session.execute(update(Menu).where(Menu.name == name_str).values(pic=new_pic))
        session.commit()
        session.close()


async def order_upd_status(fid, new_status):
    async with async_session() as session:
        status_mapping = {
            'Оплачен': 1,
            'Ожидает оплаты': 2,
            'Отменён': 3,
            'Доставлен': 4
        }
        status_value = status_mapping.get(new_status)

        if status_value is not None:
            # Логирование для отслеживания изменений
            print(f"Обновление статуса заказа {fid} на {new_status}")

            await session.execute(update(Orders).where(Orders.id == fid).values(status_id=status_value))
            await session.commit()
            print("Статус успешно обновлен")


# выборка по заказам
async def getall_client_ords():
    async with async_session() as session:
        result = await session.execute(
            select(Menu.name, Menu.price, Orders_menu.count_in_menu, Orders.order_adress, Status.status_name,
                   Orders_menu.fk_fk_order).
            select_from(Menu).
            join(Orders_menu, Orders_menu.fk_fk_menu == Menu.id).
            join(Orders, Orders_menu.fk_fk_order == Orders.id).
            join(Status, Status.id == Orders.status_id)
        )
        session.close()
    return result

#добавление в бд позиции меню
async def menu_insert(state):
    async with async_session() as session:
        try:
            async with state.proxy() as data_client:
                pic_str = data_client.get('photo')
                name_str = data_client.get('name')
                descr_str = data_client.get('description')
                price_int = data_client.get('price')
                fk_menu_groups = data_client.get('fk_menu_group')

                # Формируем словарь для новой позиции меню
                new_menu_pos = {
                    'pic': pic_str,
                    'name': name_str,
                    'description': descr_str,
                    'price': price_int,
                    'fk_menu_group': fk_menu_groups
                }

                await session.execute(insert(Menu).values(new_menu_pos))
                await session.commit()

        except Exception as e:
            print(f"Произошла ошибка при добавлении блюда в меню: {e}")
            await session.rollback()

        finally:
            await session.close()

# Создаёт пустую связь многие ко многим в Orders_menu
async def orders_menu_create_empty(ord_id):
    async with async_session() as session:
        new_row = {
            'fk_fk_order': ord_id,
            'fk_fk_menu': 1,
            'count_in_menu': 1,
        }

        await session.execute(insert(Orders_menu).values(new_row))
        await session.commit()

# Создаёт пустой заказ в Orders
async def order_create_empty(user_adress, price):
    async with async_session() as session:
        new_order = {
            'order_adress': user_adress,
            'order_date': '27.12.2023',
            'price': price,
            'status_id': 2
        }

        await session.execute(insert(Orders).values(new_order))
        await session.commit()


async def get_max_order_id():
    async with async_session() as session:
        max_id = await session.scalar(select(func.max(Orders.id)))
        return max_id

        await session.commit()

# Обновляет новые созданные строки для создания многие ко многим в Orders_menu
async def upd_new_ords_menu(dict_menu_names,ord_id):
    # for sub_dict in dict_menu_names:
        #first_key = next(iter(sub_dict.keys()))
        #dish = sub_dict[first_key]
    async with async_session() as session:
        for name in dict_menu_names.keys():
            res = await session.execute(
                select(Menu.id).
                where(Menu.name == name)
            )
            for item in res:
                tmp = item.id
                await session.execute(
                    update(Orders_menu).
                    where(Orders_menu.fk_fk_order == ord_id).
                    values(fk_fk_menu=tmp)
                )
        await session.commit()


async def order_insert(dict_names, user_adress, new_price):  # Добавляет новый заказ в таблицу
        await order_create_empty(user_adress, new_price)
        ord_id = await get_max_order_id()
        for n in range(len(dict_names)):
            await orders_menu_create_empty(ord_id)

        await upd_new_ords_menu(dict_names, ord_id)

