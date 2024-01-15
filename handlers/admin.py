from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import bot
from keyboards.inline import setup_inline_keyboard_admin, food_name
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from keyboards.admin_kb import keyboard
from src.methods import get_ad_cods, menu_delete, getall_client_ords, order_upd_status, menu_insert
from keyboards.inline import get_group_menu, fill_food_name
from unload_bd.pdf import export_to_pdf
from unload_bd.pdf import output_file, output_directory

# Заполнение словаря id, пароль через выборки из БД
ID = {}

async def fill_id_dict():
    global ID
    results = await get_ad_cods()  # Получаем данные из функции getall_ad_cods()
    ID = {item.tg_id: item.adm_password for item in results}


# список для хранения номера группы,для правильного определения команды /Загрузка
# чтобы блюда загружалось в определенную группу
fk_menu_group_list = []

# определение доступак админки
acsess_password_id = False


class FSM_admin(StatesGroup):
    password = State()
    photo = State()
    name = State()
    description = State()
    price = State()
    fk_menu_group = State()


# выход из админки
async def exit_admin(message: types.Message):
    global acsess_password_id
    acsess_password_id = False
    await bot.send_message(message.from_user.id, 'Выход из администраторской панели выполнен успешно',
                           reply_markup=ReplyKeyboardRemove())


# проверка на админа по tg id
# @dp.message_handler(commands=['admin'])
async def make_changes_access(message: types.Message):
    user_id = message.from_user.id
    await fill_id_dict()
    if user_id in ID:
        await bot.send_message(user_id, 'Введите пароль для входа в админку')
        await FSM_admin.password.set()
    else:
        await bot.send_message(user_id, 'У вас нет доступа к администраторской панели(((')


# Проверка пароля админа
# @dp.message_handler(state=FSM_admin.password)
async def check_password(message: types.Message, state: FSMContext):
    global acsess_password_id
    user_id = message.from_user.id
    entered_password = message.text
    actual_password = ID.get(user_id)
    if actual_password and entered_password == actual_password:
        acsess_password_id = True
        await bot.send_message(user_id, 'Вход в админку выполнен успешно', reply_markup=keyboard)
    else:
        await bot.send_message(user_id, 'Неверный пароль. Попробуйте еще раз.')

    await state.finish()
    await message.delete()


# @dp.message_handler(commands='Загрузить', state=None)
async def cm_start(message: types.Message):
    if acsess_password_id:
        await FSM_admin.photo.set()
        await message.reply('Загрузить фото')


# Выход из состояния
# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    if acsess_password_id:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')


# Загрузка фото при добавлении блюда
# @dp.message_handler(commands='Загрузить', state=FSM_admin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if acsess_password_id:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSM_admin.next()
        await message.reply('Введи название')


# Ввод названия
# Второй ответ пользователя и пишем в словарь
# @dp.message_handler(state=FSM_admin.name)
async def load_name(message: types.Message, state: FSMContext):
    if acsess_password_id:
        async with state.proxy() as data:
            data['name'] = message.text  # запись в словарь
        await FSM_admin.next()  # переводим боты в ожидании следующего ответа пользователя
        await message.reply("Введи описание")


# Ввод описания
# Третий ответ пользователя и пишем в словарь
# @dp.message_handler(state=FSM_admin.description)
async def load_description(message: types.Message, state: FSMContext):
    if acsess_password_id:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSM_admin.next()
        await message.reply("Укажи цену")


# Четвертый ответ пользователя и пишем в словарь
# @dp.message_handler(state=FSM_admin.price)
async def load_price(message: types.Message, state: FSMContext):
    if acsess_password_id:
        async with state.proxy() as data:
            data['price'] = float(message.text)
        await FSM_admin.next()


# Ввод цены блюда
async def load_fk_menu_group(message: types.Message, state: FSMContext):
    if acsess_password_id:
        async with state.proxy() as data:
            data['fk_menu_group'] = int(fk_menu_group_list[0])

        await menu_insert(state)  # Добавление блюда в БД

        await get_group_menu()  #
        await fill_food_name()
        await state.finish()


# @dp.message_handler(commands=['Меню'])
async def menu_admin(message: types.Message):
    if acsess_password_id:
        inl_keyboard = await setup_inline_keyboard_admin()
        await bot.send_message(message.from_user.id, 'Выберите группу:', reply_markup=inl_keyboard)


# @dp.callback_query_handler(lambda callback_query:  callback_query.data.startswith('select_group:'))
async def select_group_callback_admin(callback_query_admin: types.CallbackQuery):
    if acsess_password_id:
        global fk_menu_group_list
        group = callback_query_admin.data.split(':')[-1]
        await bot.answer_callback_query(callback_query_admin.id, text=f"Вы выбрали группу: {group}")

        name_groups = await get_group_menu()

        # Создаем словарь с номерами для групп меню
        group_numbers = {name: str(idx + 1) for idx, name in enumerate(name_groups)}
        if group in group_numbers:
            number = group_numbers[group]
            fk_menu_group_list.clear()  # Очищаем список
            fk_menu_group_list.append(number)  # Добавляем номер в списо
        else:
            print("Error")
        group_menu = food_name.get(group, [])

        if group_menu:
            for dish_info in group_menu:
                dish_photo = dish_info['Фото']
                dish_name = dish_info['Название']
                dish_desc = dish_info['Описание']
                dish_price = dish_info['Цена']
                message_text = f"{dish_name} \n {dish_desc}\nЦена: {dish_price}"
                inlbut1 = InlineKeyboardButton(text="Изменить меню",
                                               callback_data=f"update_to_table:{group}:{dish_name}")
                inlbut2 = InlineKeyboardButton(text="Удалить", callback_data=f"delete_to_table:{group}:{dish_name}")
                inline_keyboard = InlineKeyboardMarkup().add(inlbut1).add(inlbut2)
                if dish_photo:
                    await bot.send_photo(callback_query_admin.from_user.id, photo=dish_photo)
                    await bot.send_message(callback_query_admin.from_user.id, message_text,
                                           reply_markup=inline_keyboard)  # keyboard_menu.add(inline_keyboard)
        else:
            message_text = f"В группе '{group}' нет доступных блюд."
            await bot.send_message(callback_query_admin.from_user.id, message_text)


# Удаление блюда по инлайн кнопке
# @dp.message_handler(commands=['Удалить'])
async def delete_food(callback_query: types.CallbackQuery):
    if acsess_password_id:
        _, group, dish_name = callback_query.data.split(':')
        await menu_delete(dish_name)
        if group in food_name and dish_name in [d['Название'] for d in food_name[group]]:
            # Если группа и блюдо есть в словаре, удаляем блюдо из списка
            for item in food_name[group]:
                if item['Название'] == dish_name:
                    food_name[group].remove(item)
                    break  # Завершаем цикл после удаления
            await bot.answer_callback_query(callback_query.id, text=f"Блюдо {dish_name} удалено из группы: {group}")
        else:
            await bot.answer_callback_query(callback_query.id, text=f"Блюдо {dish_name} не найдено в группе: {group}")


# Изменение блюда по инлайн кнопке
# @dp.message_handler(commands=['Изменить'])
async def update_food(callback_query: types.CallbackQuery):
    if acsess_password_id:
        _, dish_name, group = callback_query.data.split(':')
        # реализация апдейт в бд
        await bot.answer_callback_query(callback_query.id, text=f"Блюдо {dish_name} изменено в группе: {group}")


# Заказы клиента
# @dp.message_handler(commands=['Просмотр заказов'])
async def orders(message: types.Message):
    if acsess_password_id:
        global previous_orders
        ords = await getall_client_ords()
        grouped_orders = {}

        for order in ords:
            if order.fk_fk_order not in grouped_orders:
                grouped_orders[order.fk_fk_order] = []

            grouped_orders[order.fk_fk_order].append(order)

        for order_id, order_info in grouped_orders.items():
            text = ""
            for order in order_info:
                text += f"Информация о заказе: {order.name}|{order.price}|{order.count_in_menu}|{order.order_adress}|{order.status_name}\n"
            inlbut1 = InlineKeyboardButton(text="Изменить статус", callback_data=f"update_status_{order_id}")
            text += "Выберите новый статус для заказа:"

            await bot.send_message(message.from_user.id, text,
                                   reply_markup=InlineKeyboardMarkup().add(inlbut1))


async def update_status_callback(query: types.CallbackQuery):
    if acsess_password_id:
        order_id = int(query.data.split('_')[-1])  # Extract the order ID from the callback data
        # Generate buttons for different status options
        buttons = [
            InlineKeyboardButton(text="Оплачен", callback_data=f"new_status_{order_id}_Оплачен"),
            InlineKeyboardButton(text="Ожидает оплаты", callback_data=f"new_status_{order_id}_Ожидает оплаты"),
            InlineKeyboardButton(text="Отменён", callback_data=f"new_status_{order_id}_Отменён"),
            InlineKeyboardButton(text="Доставлен", callback_data=f"new_status_{order_id}_Доставлен")
        ]
        keyboard = InlineKeyboardMarkup().add(*buttons)
        await query.message.edit_text("Выберите новый статус для заказа:", reply_markup=keyboard)


# Handle the new status callbacks
async def new_status_callback(query: types.CallbackQuery):
    if acsess_password_id:
        data = query.data.split('_')
        order_id = int(data[2])
        new_status = data[3]
        # Update the status
        await order_upd_status(order_id, new_status)
        await query.message.edit_text(f"Статус заказа {order_id} успешно изменён на {new_status}")

async def download_to_pdf(message: types.Message):
    await export_to_pdf(output_file, output_directory)


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_access, commands=['admin'])
    dp.register_message_handler(check_password, state=FSM_admin.password)
    dp.register_message_handler(cm_start, commands=['Загрузить'], state=None)
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSM_admin.photo)
    dp.register_message_handler(load_name, state=FSM_admin.name)
    dp.register_message_handler(load_description, state=FSM_admin.description)
    dp.register_message_handler(load_price, state=FSM_admin.price)
    dp.register_message_handler(load_fk_menu_group, state=FSM_admin.fk_menu_group)
    dp.register_message_handler(menu_admin, lambda message: 'Меню админа' == message.text)
    dp.register_callback_query_handler(select_group_callback_admin,
                                       lambda callback_query: callback_query.data.startswith('group:'))
    dp.register_callback_query_handler(delete_food,
                                       lambda callback_query: callback_query.data.startswith('delete_to_table:'))
    dp.register_callback_query_handler(update_food,
                                       lambda callback_query: callback_query.data.startswith('update_to_table:'))
    dp.register_message_handler(orders, lambda message: 'Просмотр заказов' == message.text)
    dp.register_callback_query_handler(update_status_callback, lambda query: query.data.startswith('update_status'))
    dp.register_callback_query_handler(new_status_callback, lambda query: query.data.startswith('new_status'))
    dp.register_message_handler(download_to_pdf, lambda message: 'Выгрузка бд в PDF' == message.text)
    dp.register_message_handler(exit_admin, commands=['exitadmin'])
