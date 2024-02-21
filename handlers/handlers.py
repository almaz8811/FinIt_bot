from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.keyboard import create_kb
from aiogram.filters.state import State, StatesGroup
from lexicon.lexicon import bank_list
from filters.filters import IsBankHandler

# Инициализация роутера уровня роутера
router: Router = Router()


# Создание класса, наследуемого от StatesGroup, для группы состояний FSM
class FSMFillForm(StatesGroup):
    # Создание экземпляра класса State, последовательно перечисляя возможные состояния,
    # в которых будет находиться бот в разные моменты взаимодействия с пользователем
    bank_name = State()  # Состояние ожидания выбора филиала
    balance_cash = State()  # Состояние ожидания ввода остатков по кассе
    balance_bank = State()  # Состояние ожидания ввода остатков по банку


@router.message(CommandStart())
async def process_start_command(message: Message):
    keyboard = create_kb(1, cancel_button='Отмена', **bank_list)
    await message.answer(text='Выберите организацию', reply_markup=keyboard)


@router.callback_query(F.data == 'bank_12')
async def bank_command(callback: CallbackQuery):
    await callback.message.answer(text='__bank_12__')
    await callback.message.answer(text=callback.data)


@router.callback_query(F.data == 'cancel')
async def bank_command(callback: CallbackQuery):
    await callback.message.answer(text='Действие отменено')


@router.callback_query(IsBankHandler())
async def bank_command(callback: CallbackQuery):
    await callback.message.answer(text=f'filter + {callback.data}')
