from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from keyboards.keyboard import create_kb
from lexicon.lexicon import bank_list
from filters.filters import IsBankHandler, IsDigitalFloat

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
    accept = State()  # Состояние ожидания нажатия на кнопку отправки


# Создаем базу данных:
user_dict: dict[int, dict[str, str | int | bool]] = {}


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
async def process_bank_name_sent(message: Message, state: FSMContext):
    # Сохраняем выбранный банк в хранилище по ключу "bank_name"
    await state.update_data(bank_name=message.text)
    await message.answer(text=f'Введите остатки по кассе для филиала {message.text}', reply_markup=keyboard_cancel)
    # Устанавливаем состояние ожидания ввода остатков по кассе
    await state.set_state(FSMFillForm.balance_cash)


# Это хэндлер будет срабатывать, если во время выбора филиала будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.bank_name))
async def warning_not_bank_name(message: Message):
    await message.answer(text=f'Филиал {message.text} не найден. Попробуйте выбрать другой филиал.',
                         reply_markup=keyboard_cancel)


# Этот хэндлер будет срабатывать, если введены корректные остатки по кассе
# и переводить в состояние ожидания ввода остатков по банку
@router.message(StateFilter(FSMFillForm.balance_cash), IsDigitalFloat())
async def process_balance_cash_sent(message: Message, state: FSMContext):
    # Считываем название филиала из хранилища машины состояний
    data = await state.get_data()
    # Сохраняем остатки по кассе в хранилище по ключу "balance_cash"
    await state.update_data(balance_cash=message.text)
    await message.answer(text=f'Введите остатки по банку для филиала {data.get('bank_name')}',
                         reply_markup=keyboard_cancel)
    # Устанавливаем состояние ожидания ввода остатков по банку
    await state.set_state(FSMFillForm.balance_bank)


# Это хэндлер будет срабатывать, если во время ввода остатков по кассе будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.balance_cash))
async def warning_not_balance_cash(message: Message):
    await message.answer(text=f'Неверные данные: <b>{message.text}</b>. Введите сумму остатков по кассе.',
                         parse_mode=ParseMode.HTML, reply_markup=keyboard_cancel)


# Этот хэндлер будет срабатывать, если введены корректные остатки по банку
# и переводить в состояние ожидания нажатия кнопки отправки
@router.message(StateFilter(FSMFillForm.balance_bank), IsDigitalFloat())
async def process_balance_bank_sent(message: Message, state: FSMContext):
    # Сохраняем остатки по банку в хранилище по ключу "balance_bank"
    await state.update_data(balance_bank=message.text)
    # TODO: Подставить клавиатуру с кнопками 'Отправить' и 'Отмена'
    await message.answer(text='Нажмите кнопку для отправки данных.', reply_markup=keyboard_cancel)
    # Устанавливаем состояние ожидания нажатия кнопки отправки
    await state.set_state(FSMFillForm.accept)


# Этот хэндлер будет срабатывать, если во время ввода остатков по банку будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.balance_bank))
async def warning_not_balance_bank(message: Message):
    await message.answer(text=f'Неверные данные: <b>{message.text}</b>. Введите сумму остатков по банку.',
                         parse_mode=ParseMode.HTML, reply_markup=keyboard_cancel)


# Этот хэндлер будет срабатывать на выбор кнопки подтверждения отправки данных
# и выходить из машины состояний
@router.message(F.text == 'Отправить', StateFilter(FSMFillForm.accept))
async def process_accept_sent(message: Message, state: FSMContext):
    # Добавляем в базу отправленные данные по ключу id пользователя
    user_dict[message.from_user.id] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    await message.answer(text='Спасибо! Ваши данные сохранены!\n\n'
                              'Вы вышли из машины состояний')
    # Отправляем в чат сообщение с предложением посмотреть свою анкету
    await message.answer(text='Чтобы посмотреть введенные данные отправьте команду /showdata')


# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат заполненные данные, либо сообщение об отсутствии данных
@router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata(message: Message):
    # Отправляем пользователю анкету, если она есть в базе данных
    if message.from_user.id in user_dict:
        await message.answer(text=f'Филиал: {user_dict[message.from_user.id]['bank_name']}\n'
                                  f'Остатки по кассе: {user_dict[message.from_user.id]['balance_cash']}\n'
                                  f'Остатки по банку: {user_dict[message.from_user.id]['balance_bank']}',
                             reply_markup=keyboard_start)
    else:
        # Если данных в базе нет - предлагаем заполнить
        await message.answer(text='Вы еще не вносили данные. Чтобы заполнить - выберите филиал',
                             reply_markup=keyboard_start)
    print(user_dict[message.from_user.id])


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
