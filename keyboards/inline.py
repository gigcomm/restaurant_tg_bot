from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.methods import getall_menu, getall_food_group

group_name = []
# @dp.message_handler()
async def get_group_menu():
    global group_name
    #описание логики выборки групп меню из бд
    results = await getall_food_group()
    group_name = [result.group_name for result in results]
    return group_name

food_name = {}
async def fill_food_name():
    group_names = await get_group_menu()  # Получаем список групп
    global food_name
    # Далее заполняем food_name данными из БД для каждой группы меню
    for group in group_names:
        # Получаем данные из БД для текущей группы
        data_for_group = await getall_menu(group)

        # Создаем список для текущей группы и заполняем его данными из БД
        food_list = []
        for data_item in data_for_group:
            # Создаем словарь с информацией о блюде
            food_item = {
                'Название': data_item.name,
                'Описание': data_item.description,
                'Фото': data_item.pic,
                'Цена': data_item.price
            }
            food_list.append(food_item)

        # Добавляем данные в food_name для текущей группы
        food_name[group] = food_list

    return food_name

#для клиента
async def setup_inline_keyboard():
    urlkm = InlineKeyboardMarkup(row_width=1)
    for name in group_name:
        in_b = InlineKeyboardButton(text=name, callback_data=f"select_group:{name}")
        urlkm.add(in_b)  # добавление названий групп в инлайн клавиатуру
    return urlkm

#для админки
async def setup_inline_keyboard_admin():
    urlkm_admin = InlineKeyboardMarkup(row_width=1)
    for name in group_name:
        print(name)
        in_b_admin = InlineKeyboardButton(text=name, callback_data=f"group:{name}")
        urlkm_admin.add(in_b_admin)  # добавление названий групп в инлайн клавиатуру
    return urlkm_admin
