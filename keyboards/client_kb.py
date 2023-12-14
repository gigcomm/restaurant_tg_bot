from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
#ReplyKeyboardRemove - удаление клавиатуры с кнопками(исполльзовать в хэнлерах)
button1 = KeyboardButton('\Режим работы')
button2 = KeyboardButton('\Меню')
# button3 = KeyboardButton('Поделится номером', request_contact=True)
# button4 = KeyboardButton('Поделится метоположением', request_location=True)

kd_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kd_client.add(button1).add(button2)