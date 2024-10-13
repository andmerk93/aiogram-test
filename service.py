import asyncio
# from os.path import exists
from os import getenv
# import json
# import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from dotenv import load_dotenv

from crud import get_quiz_data, get_quiz_state, set_quiz_state, Session


load_dotenv()

# Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)

# Токен, который вы получили от BotFather
API_TOKEN = getenv('API_TOKEN')

# Объект бота
bot = Bot(token=API_TOKEN)

# Диспетчер
dp = Dispatcher()

# SCORE_FILENAME = getenv('SCORE_FILENAME')
# переменная для хранения текущих результатов
CURRENT_SCORE = dict()

# QUSETIONS_FILENAME = getenv('QUSETIONS_FILENAME')
# Структура квиза
QUIZ_DATA = []


def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()
    for num, option in enumerate(answer_options):
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data=str(num)
            )
        )
    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(F.data.in_('0123'))
async def answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_id = CURRENT_SCORE.get(f'{callback.from_user.id}_level', 0)
    current_answer_id = int(callback.data)
    current_answer = QUIZ_DATA[current_question_id]['options'][current_answer_id]
    correct_anwser_id = QUIZ_DATA[current_question_id]['correct_option']
    correct_answer = QUIZ_DATA[current_question_id]['options'][correct_anwser_id]

    if current_answer_id == correct_anwser_id:
        if CURRENT_SCORE.get(f'{callback.from_user.id}_score', False):
            CURRENT_SCORE[f'{callback.from_user.id}_score'] += 1
        else:
            CURRENT_SCORE[f'{callback.from_user.id}_score'] = 1
        await callback.message.answer(f"Вы ответили {correct_answer}. Верно!")
    else:
        await callback.message.answer(
            f"Вы ответили {current_answer}. Неправильно \n"
            f"Правильный ответ: {correct_answer}"
        )

    # Обновление номера текущего вопроса в базе данных
    current_question_id += 1
    CURRENT_SCORE[f'{callback.from_user.id}_level'] = current_question_id
    await update_quiz_index()
    if current_question_id < len(QUIZ_DATA):
        await get_question(callback.message, callback.from_user.id)
    else:
        final_score = CURRENT_SCORE[f'{callback.from_user.id}_level']
        await callback.message.answer(
            "Это был последний вопрос. Квиз завершен! \n"
            f"Вы набрали {final_score} баллов"
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
    current_question_index = CURRENT_SCORE.get(f'{user_id}_level', 0)
    opts = QUIZ_DATA[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(
        f"{QUIZ_DATA[current_question_index]['question']}",
        reply_markup=kb
    )


async def new_quiz(message):
    user_id = message.from_user.id
    CURRENT_SCORE[f'{user_id}_level'] = 0
    await update_quiz_index()
    await get_question(message, user_id)


async def update_quiz_index():
    # with open(SCORE_FILENAME, 'w') as file:
    #     json.dump(CURRENT_SCORE, file)
    set_quiz_state(Session, CURRENT_SCORE)


@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    """Хэндлер на команду /quiz"""
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)


async def main():
    global CURRENT_SCORE
    CURRENT_SCORE = get_quiz_state(Session)
    # if exists(SCORE_FILENAME):
    #     global CURRENT_SCORE
    #     with open(SCORE_FILENAME) as file:
    #         CURRENT_SCORE = json.load(file)

    global QUIZ_DATA
    QUIZ_DATA = get_quiz_data(Session)
    # with open(QUSETIONS_FILENAME, encoding='utf-8') as file:
    #     QUIZ_DATA = json.load(file)

    # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
