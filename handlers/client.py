from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kd_client

# @dp.message_handler(commands=['start', 'help'])
async def command_start(message : types.Message):
 try:
    await bot.send_message(message.from_user.id, 'Приятного аппетита', reply_markup=kd_client)
    await message.delete()
 except:
    await message.reply('Общение с ботом через ЛС, напишите ему:\nhttps://t.me/Pizza_SheefBot')

# @dp.message_handler(commands=['Режим_работы'])
async def restaurant_open_command(message : types.Message):
    await bot.send_message(message.from_user.id, 'Вс-Чт с 9:00 до 20:00, Пт-Сб с 10:00 до 23:00')


def register_handler_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(restaurant_open_command, commands=['Режим_работы'])