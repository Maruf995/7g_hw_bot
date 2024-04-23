from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram import types
from PIL import Image, ImageDraw, ImageFont
from aiogram.utils import exceptions
from aiogram.types import ParseMode
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import json
import textwrap
import logging
import io
import asyncio

logging.basicConfig(level=logging.INFO)

bot = Bot('6327379626:AAFjUhmkBHcTg9DhQu5sEm-s8a5ZZ-8mcNc')
dp = Dispatcher(bot, storage=MemoryStorage())

conn = sqlite3.connect('homework.db')
cursor = conn.cursor()

photo_conn = sqlite3.connect('photos.db')
photo_cursor = photo_conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS homework
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, task TEXT)''')
conn.commit()

photo_cursor.execute('''CREATE TABLE IF NOT EXISTS photos
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, photo_path TEXT)''')
photo_conn.commit()

cursor.execute("SELECT subject, task FROM homework")
rows = cursor.fetchall()

subject_cb = CallbackData("subject", "subject_id")
delete_subject_cb = CallbackData("delete_subject", "subject_id")



admin_user_ids = [1684336348, 2118892896, 5089971653, 5095793403, 6456247158]
maruf_id = [1684336348]
lo_id = [1684336348]
user_ids = []
active_chats = {}

try:
    with open('users.json', 'r') as json_file:
        user_ids = json.load(json_file)
except FileNotFoundError:
    user_ids = []
# Загружаем список пользователей из файла, если файл существует

subjects = {
    "Русский": "Русский",
    'Литература': 'Литература',
    'Алгебра': 'Алгебра',
    'Геометрия': 'Геометрия',
    'Физика': 'Физика',
    'География': 'География',
    'Биология': 'Биология',
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

list = InlineKeyboardButton(text="Список ДЗ", callback_data="hw")
hw_btn = InlineKeyboardMarkup(row_width=1).add(list)

class SendMessageState(StatesGroup):
    InputMessage = State()

class ReportState(StatesGroup):
    WaitingForReport = State()

# class AdminChatState(StatesGroup):
#     WaitingForReply = State()

def get_subjects_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for key, value in subjects.items():
        button = InlineKeyboardButton(text=value, callback_data=subject_cb.new(subject_id=key))
        keyboard.add(button)
    return keyboard

def get_delete_subjects_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for key, value in subjects.items():
        button = InlineKeyboardButton(text=value, callback_data=delete_subject_cb.new(subject_id=key))
        keyboard.add(button)
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_ids:
        user_ids.append(user_id)
        with open('users.json', 'w') as json_file:
            json.dump(user_ids, json_file)
    await message.answer(f'Привет, {message.from_user.full_name}! ')
    await message.answer('Этот бот был создан: @maruf_proger\n'
                         'Т.К. Вы ему все надоели, Он решил создать телеграм бота.\n'
                         'Через которого можно будет в любой момент узнать Д/З.\n'
                         'А так же, задать вопрос админам и оставить жалобу', reply_markup=hw_btn)
    
@dp.message_handler(commands=['prunus'])
async def start_report(message: types.Message):
    await message.answer("ХАРА ТЕБЕ ВО ВСЕ ЩЕЛИ. Ты все так же надеешься?")

@dp.message_handler(commands=['malus'])
async def start_report(message: types.Message):
    await message.answer("АХАХАХАХХАХАХАХ, НУ ТЫ ТУПОЙ КОНЕЧНО. РАЗ ПРУНУС НЕ РАБОТАЕТ, КАКОГО ФИГА МАЛУС БУДЕТ РАБОТАТЬ?")

@dp.message_handler(commands=['report'])
async def start_report(message: types.Message):
    await message.answer("Пожалуйста, опишите вашу жалобу. Ваше сообщение будет отправлено администраторам.")
    await ReportState.WaitingForReport.set()

# Обработчик для состояния ожидания жалобы
@dp.message_handler(state=ReportState.WaitingForReport)
async def receive_report(message: types.Message, state: FSMContext):
    report_text = message.text

    # Отправляем жалобу всем админам
    for admin_id in maruf_id:
        try:
            await bot.send_message(admin_id, f"Пользователь: @{message.from_user.username} \nОправил жалобу: \n{report_text}")
        except Exception as e:
            print(f"Ошибка при отправке жалобы админам: {e}")

    await state.finish()
    await message.answer("Ваша жалоба успешно отправлена администраторам. Благодарим за ваше сообщение.")

@dp.message_handler(commands=['all'])
async def handle_send_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in admin_user_ids:
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='cancel'))
        await message.answer("Введите текст сообщения для рассылки или нажмите кнопку 'Отмена'.",
                             reply_markup=keyboard)
        await SendMessageState.InputMessage.set()  # Переходим в состояние ожидания текста сообщения
    else:
        await message.answer("Вы не являетесь администратором. Извините, у вас нет доступа к этой команде.")

@dp.callback_query_handler(lambda query: query.data == 'cancel', state=SendMessageState.InputMessage)
async def cancel_sending(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.answer("Рассылка отменена.")
    # Если вы хотите удалить клавиатуру после нажатия на кнопку Отмена
    await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id)  

@dp.message_handler(state=SendMessageState.InputMessage)
async def handle_message_input(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        await message.answer("Рассылка отменена.")
    else:
        with open('users.json', 'r') as json_file:
            user_ids = json.load(json_file)
        for user_id in user_ids:
            try:
                await bot.send_message(user_id, message.text, parse_mode=types.ParseMode.MARKDOWN)
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        await state.finish()
        await message.answer("Рассылка завершена.")


@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    await message.answer('СПИСОК ЛУЧШИХ:')
    await message.answer('АЗИЗА')
    await message.answer('МАРУФ')
    await message.answer('Саян')
    await message.answer('Вильдан')
    await message.answer('РАДМИР')
    await message.answer('БАЯН')
    await message.answer('ЧАСТИЧНО ЭЛЯ')
    await message.answer('А ОМА ТУПОЙ ИШАК')

@dp.message_handler(commands=['oma'])
async def top(message: types.Message):
    for i in range(35):
        await message.answer('ОМА ПЛОХОЙ')


@dp.message_handler(commands=['table'])
async def top(message: types.Message):
    with open('table.png', 'rb') as table_photo:
        await bot.send_photo(message.chat.id, table_photo)
    # with open('table1.png', 'rb') as table1_photo:
    #     await bot.send_photo(message.chat.id, table1_photo)
@dp.callback_query_handler(lambda query: query.data == "hw")
async def list_homework_command(callback_query: CallbackQuery):
    try:
        cursor.execute('SELECT subject, task FROM homework')
        rows = cursor.fetchall()

        # Открываем фоновое изображение
        background_image = Image.open("back.jpg").convert('RGBA')
        draw = ImageDraw.Draw(background_image)
        font_path = "font.ttf"
        font_size = 20
        font = ImageFont.truetype(font_path, font_size)
        text_color = "black"

        # Получаем размеры изображения
        image_width, image_height = background_image.size

        # Максимальное количество строк текста на одной картинке
        max_lines_per_image = 12

        # Разбиваем текст на подстроки
        text_lines = []
        for row in rows:
            subject, task = row
            wrapped_text = textwrap.fill(f'{subject}: {task}', width=39)  # Максимальная длина строки 40 символов
            text_lines.extend(wrapped_text.split('\n'))

        # Разделяем текст на несколько изображений
        for i in range(0, len(text_lines), max_lines_per_image):
            start_index = i
            end_index = i + max_lines_per_image
            lines_to_display = text_lines[start_index:end_index]

            # Создаем изображение с текстом
            text_image = Image.new('RGBA', background_image.size, (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_image)
            y_offset = 102
            for line in lines_to_display:
                text_width, text_height =  text_draw.textsize(line, font=font)
                text_draw.text((50, y_offset), line, fill=text_color, font=font)
                y_offset += text_height + 4  # Используем textsize для получения высоты текста и добавляем отступ

            # Объединяем фоновое изображение и изображение с текстом
            combined_image = Image.alpha_composite(background_image, text_image)

            # Сохраняем изображение и отправляем его пользователю
            image_bytes = io.BytesIO()
            combined_image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            await bot.send_photo(callback_query.message.chat.id, photo=image_bytes)

        await bot.send_message(callback_query.message.chat.id, 'Получить список ДЗ еще раз', reply_markup=hw_btn)

    except Exception as e:
        logging.error(f"Ошибка при получении списка домашних заданий: {e}")

@dp.message_handler(commands=['hw'])
async def list_homework_command_by_command(message: types.Message):
    try:
        cursor.execute('SELECT subject, task FROM homework')
        rows = cursor.fetchall()

        # Открываем фоновое изображение
        background_image = Image.open("back.jpg").convert('RGBA')
        draw = ImageDraw.Draw(background_image)
        font_path = "font.ttf"
        font_size = 20
        font = ImageFont.truetype(font_path, font_size)
        text_color = "black"

        # Получаем размеры изображения
        image_width, image_height = background_image.size

        # Максимальное количество строк текста на одной картинке
        max_lines_per_image = 12

        # Разбиваем текст на подстроки
        text_lines = []
        for row in rows:
            subject, task = row
            wrapped_text = textwrap.fill(f'{subject}: {task}', width=39)  # Максимальная длина строки 40 символов
            text_lines.extend(wrapped_text.split('\n'))

        # Разделяем текст на несколько изображений
        for i in range(0, len(text_lines), max_lines_per_image):
            start_index = i
            end_index = i + max_lines_per_image
            lines_to_display = text_lines[start_index:end_index]

            # Создаем изображение с текстом
            text_image = Image.new('RGBA', background_image.size, (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_image)
            y_offset = 102
            for line in lines_to_display:
                text_width, text_height =  text_draw.textsize(line, font=font)
                text_draw.text((50, y_offset), line, fill=text_color, font=font)
                y_offset += text_height + 4  # Используем textsize для получения высоты текста и добавляем отступ

            # Объединяем фоновое изображение и изображение с текстом
            combined_image = Image.alpha_composite(background_image, text_image)

            # Сохраняем изображение и отправляем его пользователю
            image_bytes = io.BytesIO()
            combined_image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            await bot.send_photo(message.chat.id, photo=image_bytes)

        await bot.send_message(message.chat.id, 'Получить список ДЗ еще раз', reply_markup=hw_btn)

    except Exception as e:
        logging.error(f"Ошибка при получении списка домашних заданий: {e}")

@dp.message_handler(commands=['delete'])
async def delete_homework_command(message: types.Message):
    user_id = message.from_user.id

    if user_id in admin_user_ids:
        await message.answer('Выберите предмет, который нужно удалить:', reply_markup=get_delete_subjects_keyboard())
    else:
        await message.answer("Вы не являетесь администратором. Извините, у вас нет доступа к этой команде.")

@dp.message_handler(commands=['clear_database'])
async def clear_database_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in maruf_id:
        try:
            cursor.execute('DELETE FROM homework')
            conn.commit()
            await message.answer("База данных успешно очищена.")
        except Exception as e:
            logging.error(f"Ошибка при очистке базы данных: {e}")
            await message.answer("Произошла ошибка при очистке базы данных.")
    else:
        await message.answer("Вы не являетесь администратором. Извините, у вас нет доступа к этой команде.")

@dp.callback_query_handler(delete_subject_cb.filter())
async def process_delete_subject_selection(callback_query: CallbackQuery, state: FSMContext):
    try:
        subject_id = callback_query.data.split(':')[-1]
        subject_name = subjects.get(subject_id)
        if subject_name:
            # Удаляем урок из базы данных
            cursor.execute('DELETE FROM homework WHERE subject = ?', (subject_id,))
            conn.commit()
            await callback_query.message.answer(f'Домашнее задание для предмета "{subject_name}" успешно удалено.')
        else:
            await callback_query.message.answer('Ошибка: предмет не найден.')
    except Exception as e:
        logging.error(f"Ошибка при удалении домашнего задания: {e}")

@dp.message_handler(commands=['add'], )
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