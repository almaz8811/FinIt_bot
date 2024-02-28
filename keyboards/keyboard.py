from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_kb(width: int, start_button: True | False = None,
              cancel_button: str | None = None, **kwargs: str) -> ReplyKeyboardMarkup:
    # Инициализация билдера
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    # Инициализация списка для кнопок
    buttons: list[KeyboardButton] = []
    # Заполнение кнопками
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(KeyboardButton(text=text))
    kb_builder.row(*buttons, width=width)
    if start_button:
        kb_builder.row(KeyboardButton(text='Выбрать филиал'))
    if cancel_button:
        kb_builder.row(KeyboardButton(text=cancel_button))
    return kb_builder.as_markup(resize_keyboard=True)
