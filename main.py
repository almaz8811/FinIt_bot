import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import handlers
from config_data.config import Config, load_config

# Инициализируем логгер
logger = logging.getLogger(__name__)

# Загрузка конфигурации в переменную config
config: Config = load_config()



# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Инициализация хранилища (создание экземпляра класса MemoryStorage)
    storage: MemoryStorage = MemoryStorage()

    # Создание объектов бота и диспетчера
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=storage)

    # Регистрация роутеров в диспетчере
    dp.include_router(handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
