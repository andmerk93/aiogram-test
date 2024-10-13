from os import getenv
from json import load

from dotenv import load_dotenv

# from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Unicode, create_engine, text

load_dotenv()
Base = declarative_base()
engine = create_engine(getenv('DB_ENGINE'))
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
        # session.commit()


# def create_tables(Session):
#     with Session.begin() as session:
#             session.add(state_query)
#             session.add(questions_query)

def create_tables_from_text(engine):
    state_query = '''
        CREATE TABLE IF NOT EXISTS "quiz_state" (
        "user_id"	INTEGER,
        "level"	INTEGER,
        "score"	INTEGER,
        PRIMARY KEY("user_id" AUTOINCREMENT)
        );
    '''

    questions_query = '''
        CREATE TABLE IF NOT EXISTS "quiz_question" (
        "id"	INTEGER,
        "question"	TEXT,
        "answer0"	TEXT,
        "answer1"	TEXT,
        "answer2"	TEXT,
        "answer3"	TEXT,
        "correct_id"	INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT)
        );
    '''
    

    with engine.connect() as conn:
        conn.execute(text(state_query))
        conn.execute(text(questions_query))


if __name__ == '__main__':
    create_tables_from_text(engine)
    # create_tables(engine)
    fill_questions(Session)

# TODO read_question, upsert_state
