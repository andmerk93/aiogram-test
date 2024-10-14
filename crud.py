from os import getenv
from json import load

from dotenv import load_dotenv

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, func, select

load_dotenv()
Base = declarative_base()
engine = create_engine(getenv('DB_ENGINE'), echo=False)
Session = sessionmaker(engine)


class Question(Base):
    __tablename__ = 'quiz_question'

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column()
    answer0: Mapped[str] = mapped_column()
    answer1: Mapped[str] = mapped_column()
    answer2: Mapped[str] = mapped_column()
    answer3: Mapped[str] = mapped_column()
    correct_id: Mapped[int] = mapped_column()

    @classmethod
    def get_total_questions(cls, Session):
        with Session() as session:
            row_count = session.scalar(select(func.count(cls.id)))
        return row_count

    @classmethod
    def get_question(cls, Session, question_id):
        return Session().get(cls, question_id)

    @classmethod
    def fill_questions(cls, Session):
        with open(getenv('QUSETIONS_FILENAME'), encoding='utf-8') as file:
            quiz_data = load(file)
        with Session.begin() as session:
            for current_question in quiz_data:
                db_question = cls(
                    question=current_question['question'],
                    answer0=current_question['options'][0],
                    answer1=current_question['options'][1],
                    answer2=current_question['options'][2],
                    answer3=current_question['options'][3],
                    correct_id=current_question['correct_option']
                )
                session.add(db_question)


class Score(Base):
    __tablename__ = 'quiz_score'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[int] = mapped_column(default=0)
    score: Mapped[int] = mapped_column(default=0)

    @classmethod
    def get_score(cls, Session, user_id):
        return Session().get(cls, user_id)

    def set_score(self, Session):
        with Session.begin() as session:
            session.merge(self)


if __name__ == '__main__':
    # create tables for first run
    Base.metadata.create_all(engine)
    Question.fill_questions(Session)
