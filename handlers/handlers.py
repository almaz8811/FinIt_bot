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
    await message.answer(text='Нажмите кнопку выбора филиала', reply_markup=keyboard_start)


# Этот хэндлер будет срабатывать на команду /cancel в любых состояниях
# кроме состояния по-умолчанию, и отключать машину состояний
@router.message(F.text == 'Отмена', ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы отменили ввод данных.\n\n'
                              'Чтобы снова перейти к заполнению - выберите филиал.',
                         reply_markup=keyboard_start)
    # Сброс состояния
    await state.clear()


# Этот хэндлер будет срабатывать на команду /cancel в состоянии по-умолчанию
# и сообщать, что эта команда доступна в машине состояний
@router.message(F.text == 'Отмена', StateFilter(default_state))
async def process_cancel_command_state(message: Message):
    await message.answer(text='Отменять нечего. Вы не вводили данных.\n\n'
                              'Чтобы перейти к заполнению - выберите филиал.',
                         reply_markup=keyboard_start)


# Этот хэндлер будет срабатывать на текст "Выбрать филиал"
# и переводить бота в состояние ожидания выбора филиала
@router.message(F.text == 'Выбрать филиал', StateFilter(default_state))
async def process_select_bank(message: Message, state: FSMContext):
    await message.answer(text='Выберите филиал', reply_markup=keyboard_bank)
    # Устанавливаем состояние ожидания выбора филиала
    await state.set_state(FSMFillForm.bank_name)


# Этот хэндлер будет срабатывать, если выбран корректный филиал
# и переводить в состояние ожидании ввода остатков по кассе
@router.message(StateFilter(FSMFillForm.bank_name), IsBankHandler())
async def process_bank_sent(message: Message, state: FSMContext):
    # Сохраняем выбранный банк в хранилище по ключу "bank"
    await state.update_data(bank=message.text)
    await message.answer(text=f'Введите остатки по кассе для филиала {message.text}', reply_markup=keyboard_cancel)
    # Устанавливаем состояние ожидания ввода остатков по кассе
    await state.set_state(FSMFillForm.balance_cash)


# Это хэндлер будет срабатывать, если во время выбора филиала будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.bank_name))
async def warning_not_bank(message: Message):
    await message.answer(text=f'Филиал {message.text} не найден. Попробуйте выбрать другой филиал.',
                         reply_markup=keyboard_cancel)


# Этот хэндлер будет срабатывать, если введены корректные остатки по кассе
# и переводить в состояние ожидания ввода остатков по банку
@router.message(StateFilter(FSMFillForm.balance_cash), F.text.isdigit())
async def process_cash_sent(message: Message, state: FSMContext):
    # Считываем название филиала из хранилища машины состояний
    data = await state.get_data()
    # Сохраняем остатки по кассе в хранилище по ключу "cash"
    await message.answer(text=f'Введите остатки по банку для филиала {data.get('bank')}',
                         reply_markup=keyboard_cancel)
    # Устанавливаем состояние ожидания ввода остатков по банку
    await state.set_state(FSMFillForm.balance_bank)


# Это хэндлер будет срабатывать, если во время ввода остатков по кассе будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.balance_cash))
async def warning_not_cash(message: Message):
    await message.answer(text=f'Неверные данные: {message.text}. Введите сумму остатков по кассе.',
                         reply_markup=keyboard_cancel)


@router.message(F.text == 'Выбрать филиал', StateFilter(default_state))
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
