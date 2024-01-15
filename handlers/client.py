from aiogram import Dispatcher
from create_bot import bot
from keyboards.client_kb import kd_client, kb_client_cart
from keyboards.inline import setup_inline_keyboard, food_name
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from src.methods import order_insert


# @dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, 'Здравствуйте! Вас приветствует бот ресторана GY',
                               reply_markup=kd_client)
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему:\n')


# @dp.message_handler(commands=['Режим работы'])
async def restaurant_open_command(message: types.Message):
    await bot.send_message(message.from_user.id, 'Вс-Чт с 9:00 до 20:00, Пт-Сб с 10:00 до 23:00')


cart = {}  # для корзины: add-to_cart()


# функция получения цены выбранного блюда
async def get_price(selected_group, dish_name):
    group = food_name.get(selected_group, [])
    for dish in group:
        if dish.get('Название') == dish_name:  # сравнение значения по ключу в словаре, с названием блюда
            return dish.get('Цена')
    return None


# @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('add_to_cart:'))
async def add_to_cart(callback_query: types.CallbackQuery):
    _, select_group, dish_name = callback_query.data.split(':')

    price = await get_price(select_group, dish_name)

    if dish_name not in cart:
        cart[dish_name] = {'price': price, 'quantity': 1}
    else:
        cart[dish_name]['quantity'] += 1

    await bot.answer_callback_query(callback_query.id, text=f"Добавлено в корзину: {dish_name}")


# @dp.messagw_handler(commads=['Корзина'])
async def cart_food(message: types.Message):
    if not cart:
        await bot.send_message(message.from_user.id, "Ваша корзина пуста.")
    else:
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())
        for name, price in cart.items():
            cart_text = f"Ваша корзина:\n{name}:\n Цена: {price['price']} * Количество: {price['quantity']}" \
                        f" = {price['price'] * price['quantity']}\n"

            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton(text='Увеличить количество', callback_data=f"increase_quantity:{name}"),
                InlineKeyboardButton(text='Уменьшить количество', callback_data=f"decrease_quantity:{name}"),
                InlineKeyboardButton(text='Удалить', callback_data=f"remove_from_cart:{name}"))
            cart_text += f"\t\tИтого: {total_price}"
            await bot.send_message(message.from_user.id, cart_text, reply_markup=keyboard)
        await bot.send_message(message.from_user.id, "Дополнительные опции:", reply_markup=kb_client_cart)


# @dp.callback_query_handler(lambda callback_query:  callback_query.data.startswith('increase_quantity:',
# 'decrease_quantity:', 'remove_from_cart:')
async def handler_cart_action(callback_query: types.CallbackQuery):
    action, dish_name = callback_query.data.split(':')
    if action == 'increase_quantity':
        cart[dish_name]['quantity'] += 1
        await bot.answer_callback_query(callback_query.id, text=f"Количество {dish_name} увеличено на 1")
    elif action == 'decrease_quantity':
        if cart[dish_name]['quantity'] > 1:
            cart[dish_name]['quantity'] -= 1
            await bot.answer_callback_query(callback_query.id, text=f"Количество {dish_name} уменьшено на 1")
        else:
            await bot.answer_callback_query(callback_query.id, text=f"Количество {dish_name} не может быть меньше 1")
    elif action == 'remove_from_cart':
        del cart[dish_name]
        await bot.answer_callback_query(callback_query.id, text=f"{dish_name} удален из корзины")


orders = {}  # Создаем пустой словарь для хранения заказов


class OrderProcessStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()


# Шаг 2: Обработка нажатия кнопки и запрос имени пользователя
# @dp.message_handler(lambda message: message.text == 'Сделать заказ')
async def process_order_start(message: types.Message):
    await bot.send_message(message.from_user.id, "Для оформления заказа, укажите ваше имя:")
    await OrderProcessStates.waiting_for_name.set()


# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


# Шаг 3: Получение имени пользователя
# @dp.message_handler(state=OrderProcessStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    async with state.proxy() as data_client:
        data_client['name'] = name
    await OrderProcessStates.next()
    await bot.send_message(message.from_user.id, "Теперь укажите ваш номер телефона:")
    await OrderProcessStates.waiting_for_phone.set()


# Шаг 4: Получение номера телефона
# @dp.message_handler(state=OrderProcessStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    async with state.proxy() as data_client:
        data_client['phone'] = phone
    await OrderProcessStates.next()
    await bot.send_message(message.from_user.id, "Укажите ваш адрес:")
    await OrderProcessStates.waiting_for_address.set()


# Шаг 5: Получение адреса и добавление заказа в словарь
# @dp.message_handler(state=OrderProcessStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    adress = message.text
    async with state.proxy() as data_client:
        data_client['adress'] = adress
    await bot.send_message(message.from_user.id, "Ваш заказ оформлен!")

    def calculate_total_price(cart):
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())
        return total_price

    total = calculate_total_price(cart)
    async with state.proxy() as data_client:
        await order_insert(cart, data_client.get('adress'), total)
    cart.clear()

    await state.finish()  # Завершаем FSM


# @dp.message_handler(commads=['Мои заказы'])
async def my_order_food(message: types.Message):
    pass


# @dp.message_handler(commands=['Меню'])
async def menu(message: types.Message):
    inl_keyboard = await setup_inline_keyboard()
    await bot.send_message(message.from_user.id, 'Выберите группу:', reply_markup=inl_keyboard)


# @dp.callback_query_handler(lambda callback_query:  callback_query.data.startswith('select_group:'))
async def select_group_callback(callback_query: types.CallbackQuery):
    selected_group = callback_query.data.split(':')[-1]
    await bot.answer_callback_query(callback_query.id, text=f"Вы выбрали группу: {selected_group}")
    group_menu = food_name.get(selected_group, [])

    if group_menu:
        for dish_info in group_menu:
            dish_photo = dish_info['Фото']
            dish_name = dish_info['Название']
            dish_desc = dish_info['Описание']
            dish_price = dish_info['Цена']
            message_text = f"\n{dish_name}\n{dish_desc}\nЦена: {dish_price}"
            inlbut = InlineKeyboardButton(text="Добавить в корзину",
                                          callback_data=f"add_to_cart:{selected_group}:{dish_name}")
            if dish_photo:
                await bot.send_photo(callback_query.from_user.id, photo=dish_photo)
            await bot.send_message(callback_query.from_user.id, message_text,
                                   reply_markup=InlineKeyboardMarkup().add(inlbut))
    else:
        message_text = f"В группе '{selected_group}' нет доступных блюд."
        await bot.send_message(callback_query.from_user.id, message_text)


# Регистрация хендлеров(вызов команд)
def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(restaurant_open_command, lambda message: 'Режим работы' in message.text)
    dp.register_message_handler(cart_food, lambda message: 'Корзина' == message.text)
    dp.register_message_handler(my_order_food, lambda message: 'Мои заказы' == message.text)
    dp.register_message_handler(menu, lambda message: 'Меню' == message.text)

    dp.register_callback_query_handler(handler_cart_action, lambda callback_query: callback_query.data.startswith(
        ('increase_quantity:', 'decrease_quantity:', 'remove_from_cart:')))
    dp.register_callback_query_handler(select_group_callback,
                                       lambda callback_query: callback_query.data.startswith('select_group:'))
    dp.register_callback_query_handler(add_to_cart,
                                       lambda callback_query: callback_query.data.startswith('add_to_cart:'))
    dp.register_message_handler(process_order_start, lambda message: 'Сделать заказ' == message.text, state=None)
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(process_name, state=OrderProcessStates.waiting_for_name)
    dp.register_message_handler(process_phone, state=OrderProcessStates.waiting_for_phone)
    dp.register_message_handler(process_address, state=OrderProcessStates.waiting_for_address)
