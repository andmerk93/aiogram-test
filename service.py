import asyncio
from os import getenv
# import logging

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from dotenv import load_dotenv

from crud import Session, Score, Question


load_dotenv()

# Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)

# Токен, который вы получили от BotFather
API_TOKEN = getenv('API_TOKEN')

# Объект бота
bot = Bot(token=API_TOKEN)

# Диспетчер
dp = Dispatcher()

router = Router()

dp.include_router(router)


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


@router.callback_query(F.data.in_('0123'))
async def answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_score = await Score.get_score(Session, user_id=callback.from_user.id)

    current_question_id = current_score.level + 1
    current_question = await Question.get_question(Session, current_question_id)

    current_answer_id = int(callback.data)
    current_answer = getattr(current_question, f'answer{current_answer_id}')

    correct_anwser_id = current_question.correct_id
    correct_answer = getattr(current_question, f'answer{correct_anwser_id}')

    if current_answer_id == correct_anwser_id:
        current_score.score += 1
        await callback.message.answer(f"Вы ответили {correct_answer}. Верно!")
    else:
        await callback.message.answer(
            f"Вы ответили {current_answer}. Неправильно \n"
            f"Правильный ответ: {correct_answer}"
        )

    # Обновление номера текущего вопроса
    current_score.level += 1
    await current_score.set_score(Session)
    if current_score.level < TOTAL_QUIZ_QUESTIONS:
        await get_question(callback.message, current_score.level)
    else:
        await callback.message.answer(
            "Это был последний вопрос. Квиз завершен! \n"
            f"Вы набрали {current_score.score} баллов"
        )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Хэндлер на команду /start"""
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer(
        "Добро пожаловать в квиз!",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


async def get_question(message, current_index):
    """Получение текущего вопроса"""
    question = await Question.get_question(Session, current_index + 1)
    opts = [
        question.answer0,
        question.answer1,
        question.answer2,
        question.answer3,
    ]
    kb = generate_options_keyboard(opts)
    await message.answer(
        question.question,
        reply_markup=kb
    )


async def new_quiz(message):
    user_id = message.from_user.id
    user_state = Score(
        user_id=user_id,
        level=0,
    )
    await user_state.set_score(Session)
    await get_question(message, 0)


@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    """Хэндлер на команду /quiz"""
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)


async def main():
    global TOTAL_QUIZ_QUESTIONS
    TOTAL_QUIZ_QUESTIONS = await Question.get_total_questions(Session)

    # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
