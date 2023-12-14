from aiogram import types, Dispatcher
from create_bot import dp

#всегда последний
# @dp.message_handler()
async def echo_send(message : types.Message):
    await message.answer(message.text)
    # await message.reply(message.text)
    # await bot.send_message(message.from_user.id, message.text)


def register_handler_other(dp : Dispatcher):
    dp.register_message_handler(echo_send)