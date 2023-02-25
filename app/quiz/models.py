from dataclasses import dataclass

from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Theme:
    id: int | None
    title: str


@dataclass
class Answer:
    title: str
    is_correct: bool


@dataclass
class Question:
    id: int | None
    title: str
    theme_id: int
    answers: list[Answer] | None


class ThemeModel(db):
    __tablename__ = "themes"
    id = Column(BigInteger, primary_key=True)
    title = Column(String, unique=True, nullable=False)

    def convert_to_dc(self):
        return Theme(
            id=self.id,
            title=self.title
        )

class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    theme_id = Column(BigInteger, ForeignKey('themes.id', ondelete="CASCADE"), nullable=False)

    def convert_to_dc(self):
        return Question(
            id=self.id,
            title=self.title,
            theme_id=self.theme_id,
            answers=[a.convert_to_dc() for a in self.answers]
        )

class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    is_correct = Column(Boolean)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="CASCADE"))
    question = relationship("QuestionModel", backref="answers")

    def convert_to_dc(self):
        return Answer(
            title=self.title,
            is_correct=self.is_correct
        )



