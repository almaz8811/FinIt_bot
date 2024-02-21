from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class IsBankHandler(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        print(callback.data)
        return callback.data.startswith('bank')
