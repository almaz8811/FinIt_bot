from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_kb(width: int, cancel_button: str | None = None, **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализация билдера
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализация списка для кнопок
    buttons: list[InlineKeyboardButton] = []
    # Заполнение кнопками
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text=text, callback_data=button))
    kb_builder.row(*buttons, width=width)
    if cancel_button:
        kb_builder.row(InlineKeyboardButton(text=cancel_button, callback_data='cancel'))
    return kb_builder.as_markup()