from aiogram.filters import BaseFilter
from aiogram.types import Message
from lexicon.lexicon import bank_list


class IsBankHandler(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        print(message.text in bank_list.values())
        return message.text in bank_list.values()
