from aiogram.utils import executor
from create_bot import dp

async def on_startup(_):
    print('Бот запущен')

from handlers import admin, client, other

client.register_handler_client(dp)
other.register_handler_other(dp) #всегда последняя

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)