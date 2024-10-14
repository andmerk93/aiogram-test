from os import getenv
from json import load

from dotenv import load_dotenv

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

engine = create_async_engine(getenv('DB_ENGINE'), echo=False)
Session = async_sessionmaker(engine)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class Question(Base):
    __tablename__ = 'quiz_question'

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str]
    answer0: Mapped[str]
    answer1: Mapped[str]
    answer2: Mapped[str]
    answer3: Mapped[str]
    correct_id: Mapped[int]

    @classmethod
    async def get_total_questions(cls, Session):
        async with Session() as session:
            row_count = await session.scalar(select(func.count(cls.id)))
        return row_count

    @classmethod
    async def get_question(cls, Session, question_id):
        return await Session().get(cls, question_id)

    @classmethod
    async def fill_questions(cls, Session):
        with open(getenv('QUSETIONS_FILENAME'), encoding='utf-8') as file:
            quiz_data = load(file)
        async with Session.begin() as session:
            session.add_all([
                cls(
                    question=current_question['question'],
                    answer0=current_question['options'][0],
                    answer1=current_question['options'][1],
                    answer2=current_question['options'][2],
                    answer3=current_question['options'][3],
                    correct_id=current_question['correct_option']
                )
                for current_question in quiz_data
            ])


class Score(Base):
    __tablename__ = 'quiz_score'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[int] = mapped_column(default=0)
    score: Mapped[int] = mapped_column(default=0)

    @classmethod
    async def get_score(cls, Session, user_id):
        return await Session().get(cls, user_id)

    async def set_score(self, Session):
        async with Session.begin() as session:
            session.merge(self)


async def first_run():
    """create and fill tables for first run"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await Question.fill_questions(Session)

if __name__ == '__main__':
    from asyncio import run
    run(first_run())
