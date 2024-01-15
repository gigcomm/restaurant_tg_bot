from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('Меню админа')
b2 = KeyboardButton('Просмотр заказов')
b3 = KeyboardButton('Загрузить')
b4 = KeyboardButton('Выгрузка бд в PDF')
b5 = KeyboardButton('Выгрузка бд в Excel')
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(b1).add(b2).add(b4)

keyboard_menu = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_menu.add(b3)
