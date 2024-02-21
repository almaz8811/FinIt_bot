from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from keyboards.keyboard import create_kb
from lexicon.lexicon import bank_list
from filters.filters import IsBankHandler

# Инициализация роутера уровня роутера
router: Router = Router()

keyboard_bank = create_kb(1, cancel_button='Отмена', **bank_list)
keyboard_cancel = create_kb(1, cancel_button='Отмена')

# Создание класса, наследуемого от StatesGroup, для группы состояний FSM
class FSMFillForm(StatesGroup):
    # Создание экземпляра класса State, последовательно перечисляя возможные состояния,
    # в которых будет находиться бот в разные моменты взаимодействия с пользователем
    bank_name = State()  # Состояние ожидания выбора филиала
    balance_cash = State()  # Состояние ожидания ввода остатков по кассе
    balance_bank = State()  # Состояние ожидания ввода остатков по банку


# Этот хэндлер будет срабатывать на команду /start и отправлять в чат клавиатуру с кнопками
@router.message(CommandStart())
async def process_start_command(message: Message):
    # Передать весь словарь bank_list с кнопками
    await message.answer(text='Выберите организацию', reply_markup=keyboard_bank)


# Этот хэндлер будет срабатывать на команду /cancel в любых состояниях
# кроме состояния по-умолчанию, и отключать машину состояний
@router.callback_query(F.data == 'cancel', ~StateFilter(default_state))
async def process_cancel_command_state(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Вы отменили ввод данных\n\n'
                                       'Чтобы снова перейти к заполнению - выберите филиал')
    await callback.message.delete()


# # Этот хэндлер будет срабатывать на команду /cancel в состоянии по-умолчанию
# # и сообщать, что эта команда доступна в машине состояний
# @router.callback_query(F.data == 'cancel', StateFilter)
# async def process_cancel_command(callback: CallbackQuery):


@router.callback_query(F.data == 'bank_12')
async def bank_command(callback: CallbackQuery):
    await callback.message.answer(text='Вы отменили ввод данных\n'
                                       'Чтобы снова перейти к заполнению - выберите филиал',
                                  reply_markup=keyboard_cancel)
    await callback.message.delete()


@router.callback_query(F.data == 'cancel')
async def bank_command(callback: CallbackQuery):
    await callback.message.answer(text='Вы отменили ввод данных\n'
                                       'Чтобы снова перейти к заполнению - выберите филиал',
                                  reply_markup=keyboard_bank)
    await callback.message.delete()


@router.callback_query(IsBankHandler())
async def bank_command(callback: CallbackQuery):
    await callback.message.answer(text=f'filter + {callback.data}', reply_markup=keyboard_bank)
    await callback.message.delete()
