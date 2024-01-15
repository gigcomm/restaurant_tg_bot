from aiogram import types, Dispatcher
from create_bot import bot


# всегда последний
# @dp.message_handler()
async def echo_send(message: types.Message):
    await bot.send_message(message.from_user.id, 'Я тебя не понимаю.\nВведи команду /start или /help')

def register_handler_other(dp: Dispatcher):
    dp.register_message_handler(echo_send)
