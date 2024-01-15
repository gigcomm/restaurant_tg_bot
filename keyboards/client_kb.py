from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


button1 = KeyboardButton('Режим работы')
button2 = KeyboardButton('Меню')
button3 = KeyboardButton('Корзина')
button8 = KeyboardButton('Сделать заказ')
button9 = KeyboardButton('Отмена')

kd_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_cart = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client_order = ReplyKeyboardMarkup(resize_keyboard=True)
kd_client.add(button2).add(button3).row(button1)
kb_client_cart.add(button8).add(button3).add(button2)

