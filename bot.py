from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram import types
from PIL import Image, ImageDraw, ImageFont
import io
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import logging


logging.basicConfig(level=logging.INFO)

bot = Bot('6569715162:AAELzdCadg1BCKpNxNYoplAYzYSKI4CsgFs')
dp = Dispatcher(bot, storage=MemoryStorage())

conn = sqlite3.connect('homework.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS homework
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, task TEXT)''')
rows = cursor.fetchall()
conn.commit()

subject_cb = CallbackData("subject", "subject_id")

admin_user_ids = [1684336348, 1121073609, 2118892896, 5089971653]

subjects = {
    "Русский": "Русский",
    'Литература': 'Литература',
    'Алгебра': 'Алгебра',
    'Геометрия': 'Геометрия',
    'Физика': 'Физика',
    'География': 'География',
    "Английский (1)": "Английский (1 группа)",
    'Английский шк (1)': 'Английский ШК Компонент (1 группа)',
    'Английский (2)': 'Английский (2 группа)',
    'Английский шк (2)': 'Английский ШК Компонент (2 группа)',
    'Кырг (1) ': 'Кырг (1 группа)',
    'Кырг (2) ': 'Кырг (2 группа)',
    'Адабиат': 'Адабиат',
    'История': 'История',
    'ЧиО': 'ЧиО',
    'Музыка': 'Музыка',
    'Информатика (1 группа)': 'Информатика (1 группа)',
    'Информатика (2 группа)': 'Информатика (2 группа)',
    'ИЗО': 'ИЗО'
}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}! ')
    await message.answer('Этот бот был создан: @maruf_proger\n'
                         'Т.К. Вы ему все надоели, Он решил создать телеграм бота.\n'
                         'Через которого можно будет в любой момент узнать Д/З.\n'
                         'А так же, задать вопрос админам и оставить жалобу')

@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    await message.answer('СПИСОК ЛУЧШИХ:')
    await message.answer('АЗИЗА')
    await message.answer('МАРУФ')
    await message.answer('РАДМИР')
    await message.answer('БАЯН')
    await message.answer('ЧАСТИЧНО ЭЛЯ')
    await message.answer('А ОМА ТУПОЙ ИШАК')

@dp.message_handler(commands=['list'])
async def list_homework_command(message: types.Message):
    try:
        cursor.execute('SELECT subject, task FROM homework')
        rows = cursor.fetchall()

        # Создаем изображение
        image = Image.new('RGB', (400, 200), color='white')
        d = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # Добавляем данные на изображение

        y_offset = 10
        for row in rows:
            subject, task = row
            text = f'{subject}: {task}'
            d.text((10, y_offset), text, fill='black', font=font)
            y_offset += 20

        # Сохраняем изображение в байтовом формате
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        # Отправляем изображение пользователю
        await bot.send_photo(message.chat.id, photo=image_bytes)

    except Exception as e:
        logging.error(f"Ошибка при получении списка домашних заданий: {e}")


def get_subjects_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for key, value in subjects.items():
        button = InlineKeyboardButton(text=value, callback_data=subject_cb.new(subject_id=key))
        keyboard.add(button)
    return keyboard

@dp.message_handler(commands=['add'])
async def add_homework_command(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in admin_user_ids:
        await message.answer('Выберите предмет, для которого нужно добавить домашнее задание:', reply_markup=get_subjects_keyboard())
    else:
        await message.answer("Вы не являетесь администратором. Извините, у вас нет доступа к этой команде.")

@dp.callback_query_handler(subject_cb.filter())
async def process_subject_selection(callback_query: CallbackQuery, state: FSMContext):
    try:
        subject_id = callback_query.data.split(':')[-1]  # Извлекаем subject_id из данных обратного вызова
        subject_name = subjects.get(subject_id)
        if subject_name:
            # Сохраняем выбранный предмет в состоянии
            async with state.proxy() as data:
                data['subject'] = subject_id  # Store the subject ID in the state
            await callback_query.message.answer(f'Введите домашнее задание для предмета "{subject_name}": ')
        else:
            await callback_query.message.answer('Ошибка: предмет не найден.')
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса обратного вызова: {e}")


@dp.message_handler(state="*")
async def save_homework(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        if user_id in admin_user_ids:
            async with state.proxy() as data:
                subject_id = data.get('subject')
            if subject_id:
                task = message.text
                # Проверяем, существует ли уже запись для данного предмета
                cursor.execute('SELECT * FROM homework WHERE subject = ?', (subject_id,))
                existing_record = cursor.fetchone()
                if existing_record:
                    # Если запись существует, обновляем задание (task)
                    cursor.execute('UPDATE homework SET task = ? WHERE subject = ?', (task, subject_id))
                else:
                    # Если записи нет, создаем новую запись
                    cursor.execute('INSERT INTO homework (subject, task) VALUES (?, ?)', (subject_id, task))
                conn.commit()
                await state.finish()  # Завершаем FSM состояние
                await message.answer(f"Домашнее задание успешно обновлено.")
        else:
            await message.answer("Вы не являетесь администратором. Извините, у вас нет доступа к этой команде.")
    except Exception as e:
        logging.error(f"Ошибка при обновлении/сохранении домашнего задания: {e}")



if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)