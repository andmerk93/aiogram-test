from os import getenv
from json import load

from dotenv import load_dotenv

# from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Unicode, create_engine, select

load_dotenv()
Base = declarative_base()
engine = create_engine(getenv('DB_ENGINE'), echo=False)
Session = sessionmaker(engine)


class Question(Base):
    __tablename__ = 'quiz_question'

    id = Column(Integer, primary_key=True)
    question = Column(Unicode)
    answer0 = Column(Unicode)
    answer1 = Column(Unicode)
    answer2 = Column(Unicode)
    answer3 = Column(Unicode)
    correct_id = Column(Integer)


class State(Base):
    __tablename__ = 'quiz_state'

    user_id = Column(Integer, primary_key=True)
    level = Column(Integer)
    score = Column(Integer)


def fill_questions(Session):
    QUSETIONS_FILENAME = getenv('QUSETIONS_FILENAME')
    with open(QUSETIONS_FILENAME, encoding='utf-8') as file:
        quiz_data = load(file)
    with Session.begin() as session:
        for current_question in quiz_data:
            db_question = Question(
                question=current_question['question'],
                answer0=current_question['options'][0],
                answer1=current_question['options'][1],
                answer2=current_question['options'][2],
                answer3=current_question['options'][3],
                correct_id=current_question['correct_option']
            )
            session.add(db_question)


def get_quiz_data(Session):
    with Session() as session:
        questions = session.scalars(select(Question)).all()
    return [
        dict(
            question=current_question.question,
            options=[
                current_question.answer0,
                current_question.answer1,
                current_question.answer2,
                current_question.answer3,
            ],
            correct_option=current_question.correct_id
        )
        for current_question in questions
    ]


def get_quiz_state(Session):
    scores_dict = dict()
    with Session() as session:
        for score in session.scalars(select(State)).all():
            scores_dict[f'{score.user_id}_score'] = score.score
            scores_dict[f'{score.user_id}_level'] = score.level
    return scores_dict


def set_quiz_state(Session, quiz_state):
    temp_quiz_state = dict()
    for key, val in quiz_state.items():
        id, param = key.split('_')
        if id not in temp_quiz_state:
            temp_quiz_state[id] = dict()
        temp_quiz_state[id][param] = val
    with Session.begin() as session:
        for id, params in temp_quiz_state.items():
            session.merge(
                State(
                    user_id=id,
                    level=params['level'],
                    score=params['score'],
                )
            )


if __name__ == '__main__':
    # create tables for first run
    # Base.metadata.create_all(engine)
    # fill_questions(Session)
    print(get_quiz_data(Session), sep='\n')

# TODO read_question, upsert_state
