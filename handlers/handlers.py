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

keyboard_start = create_kb(1, start_button=True)
keyboard_bank = create_kb(1, cancel_button='Отмена', **bank_list)
keyboard_cancel = create_kb(1, cancel_button='Отмена')


# Создание класса, наследуемого от StatesGroup, для группы состояний FSM
class FSMFillForm(StatesGroup):
    # Создание экземпляра класса State, последовательно перечисляя возможные состояния,
    # в которых будет находиться бот в разные моменты взаимодействия с пользователем
    bank_name = State()  # Состояние ожидания выбора филиала
    balance_cash = State()  # Состояние ожидания ввода остатков по кассе
    balance_bank = State()  # Состояние ожидания ввода остатков по банку


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать выбрать филиал
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    # Передать весь словарь bank_list с кнопками
    await message.answer(text='Внести остатки', reply_markup=keyboard_start)


# Этот хэндлер будет срабатывать на команду /cancel в любых состояниях
# кроме состояния по-умолчанию, и отключать машину состояний
@router.message(F.text == 'Отмена', ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы отменили ввод данных.\n\n'
                              'Чтобы снова перейти к заполнению - выберите филиал.',
                         reply_markup=keyboard_bank)
    # Сброс состояния
    await state.clear()


# Этот хэндлер будет срабатывать на команду /cancel в состоянии по-умолчанию
# и сообщать, что эта команда доступна в машине состояний
@router.message(F.text == 'Отмена', StateFilter(default_state))
async def process_cancel_command_state(message: Message, ):
    await message.answer(text='Отменять нечего. Вы не вводили данных.\n\n'
                              'Чтобы перейти к заполнению - выберите филиал.',
                         reply_markup=keyboard_bank)


@router.message(F.text == 'test')
async def bank_command(message: Message):
    await message.answer(text='Вы отменили ввод данных\n\n'
                              'Чтобы снова перейти к заполнению - выберите филиал',
                         reply_markup=keyboard_cancel)


@router.message(F.text == 'Отмена')
async def bank_command(message: Message):
    await message.answer(text='Вы отменили ввод данных\n'
                              'Чтобы снова перейти к заполнению - выберите филиал',
                         reply_markup=keyboard_bank)


@router.message(IsBankHandler())
async def bank_command(message: Message):
    await message.answer(text=f'Выбран филиал {message.text}', reply_markup=keyboard_bank)
