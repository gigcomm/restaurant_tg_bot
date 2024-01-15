from aiogram.utils import executor
from create_bot import dp
from src.config import async_main
from keyboards.inline import get_group_menu, fill_food_name


async def on_startup(_):
    try:

        await async_main()
        await get_group_menu()
        await fill_food_name()

        print('Соединение к бд успешно')
    except Exception as e:
        print(f'Ошибка: {e}')
    print('Бот запущен')

from handlers import admin, client, other

client.register_handler_client(dp)
admin.register_handlers_admin(dp)
other.register_handler_other(dp) #всегда последняя

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)