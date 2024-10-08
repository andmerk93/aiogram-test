import asyncio
from os.path import exists
from os import getenv
import json
# import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from dotenv import load_dotenv


load_dotenv()

# Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)

# Токен, который вы получили от BotFather
API_TOKEN = getenv('API_TOKEN')

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

SCORE_FILENAME = getenv('SCORE_FILENAME')
# переменная для хранения текущих результатов
CURRENT_SCORE = dict()

QUSETIONS_FILENAME = getenv('QUSETIONS_FILENAME')
# Структура квиза
QUIZ_DATA = []


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data=(
                    "right_answer"
                    if option == right_answer
                    else "wrong_answer"
                )
            )
        )
    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await answer(callback, 'right_answer')


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await answer(callback, 'wrong_answer')


async def answer(callback: types.CallbackQuery, answer_status: str):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = CURRENT_SCORE.get(callback.from_user.id, 0)
    if answer_status == 'right_answer':
        await callback.message.answer("Верно!")
    else:
        # Получение текущего вопроса из словаря состояний пользователя
        correct_option = QUIZ_DATA[current_question_index]['correct_option']
        await callback.message.answer(
            "Неправильно. Правильный ответ: "
            f"{QUIZ_DATA[current_question_index]['options'][correct_option]}"
        )

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    CURRENT_SCORE[callback.from_user.id] = current_question_index
    await update_quiz_index()
    if current_question_index < len(QUIZ_DATA):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(
            "Это был последний вопрос. Квиз завершен!"
        )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Хэндлер на команду /start"""
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer(
        "Добро пожаловать в квиз!",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


async def get_question(message, user_id):
    """Получение текущего вопроса из словаря состояний пользователя"""
    current_question_index = CURRENT_SCORE.get(user_id, 0)
    correct_index = QUIZ_DATA[current_question_index]['correct_option']
    opts = QUIZ_DATA[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(
        f"{QUIZ_DATA[current_question_index]['question']}",
        reply_markup=kb
    )


async def new_quiz(message):
    user_id = message.from_user.id
    CURRENT_SCORE[user_id] = 0
    await update_quiz_index()
    await get_question(message, user_id)


async def update_quiz_index():
    """
    key - user_id
    value - question_index
    """
    # TODO: async with file
    with open(SCORE_FILENAME, 'w') as file:
        json.dump(CURRENT_SCORE, file)


@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    """Хэндлер на команду /quiz"""
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)


async def main():
    if exists(SCORE_FILENAME):
        global CURRENT_SCORE
        with open(SCORE_FILENAME) as file:
            CURRENT_SCORE = json.load(file)

    global QUIZ_DATA
    with open(QUSETIONS_FILENAME, encoding='utf-8') as file:
        QUIZ_DATA = json.load(file)

    # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
