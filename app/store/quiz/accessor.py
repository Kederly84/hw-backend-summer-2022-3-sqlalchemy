# from app.base.base_accessor import BaseAccessor
# from app.quiz.models import (
#     Answer,
#     Question,
#     Theme, ThemeModel, QuestionModel, AnswerModel
# )
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload
#
#
# class QuizAccessor(BaseAccessor):
#
#     async def create_theme(self, title: str) -> Theme:
#         theme = ThemeModel(title=title)
#         async with self.app.database.session() as connection:
#             print(theme)
#             connection.add(theme)
#             await connection.commit()
#         return theme.convert_to_dc()
#
#     async def get_theme_by_title(self, title: str) -> Theme | None:
#         async with self.app.database.session() as connection:
#             result = await connection.execute(
#                 select(ThemeModel).where(ThemeModel.title == title).scalar().one()
#             )
#             if result is not None:
#                 return result.convert_to_dc()
#
#     async def get_theme_by_id(self, id_: int) -> Theme | None:
#         async with self.app.database.session() as connection:
#             result = await connection.execute(
#                 select(ThemeModel).where(ThemeModel.id == id_).scalar().one()
#             )
#             if result is not None:
#                 return result.convert_to_dc()
#
#     async def list_themes(self) -> list[Theme]:
#         async with self.app.database.session() as session:
#             result = await session.execute(select(ThemeModel))
#             raw_res = [Theme(id=r.id, title=r.title) for r in result.scalars()]
#             return raw_res
#
#     async def create_answers(
#             self, question_id: int, answers: list[Answer]
#     ) -> list[Answer]:
#         raw_answers = [
#             AnswerModel(
#                 question_id=question_id,
#                 title=answer.title,
#                 is_correct=answer.is_correct
#             ) for answer in answers
#         ]
#         async with self.app.database.session() as connection:
#             connection.add_all(raw_answers)
#             await connection.commit()
#         return raw_answers
#
#     async def create_question(
#             self, title: str, theme_id: int, answers: list[Answer]
#     ) -> Question:
#         question = QuestionModel(title=title, theme_id=theme_id)
#         async with self.app.database.session() as connection:
#             connection.add(question)
#             await connection.commit()
#         raw_answers = await self.create_answers(question_id=question.id, answers=answers)
#         question.answers = raw_answers
#         return question.convert_to_dc()

    # async def get_question_by_title(self, title: str) -> Question | None:
    #     async with self.app.database.session() as connection:
    #         result = await connection.execute(
    #             select(QuestionModel).where(QuestionModel.title == title).scalar().one()
    #         )
    #         result.answer = await connection.execute(
    #             select(AnswerModel).where(AnswerModel.question_id == result.id).scalars())
    #         if result is not None:
    #             return result.convert_to_dc()
    #
    # async def list_questions(self, theme_id: int | None = None) -> list[Question]:
    #     async with self.app.database.session() as connection:
    #         if theme_id:
    #             result = await connection.execute(
    #                 select(QuestionModel).where(QuestionModel.theme_id == theme_id))
    #         else:
    #             result = await connection.execute(select(QuestionModel))
    #         some_res = result.scalars()
    #         another_res = []
    #         for res in some_res:
    #             answers = await connection.execute(select(AnswerModel).where(AnswerModel.question_id == res.id))
    #             res.answers = answers.scalars()
    #             another_res.append(res)
    #     raw_res = [res.convert_to_dc() for res in another_res]
    #     print(raw_res)
    #     return raw_res

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Answer,
    Question,
    Theme,
    ThemeModel,
    QuestionModel,
    AnswerModel
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        async with self.app.database.session() as session:
            theme = ThemeModel(title=title)
            session.add(theme)
            await session.commit()
            return theme.convert_to_dc()

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        async with self.app.database.session() as session:
            q = select(ThemeModel).where(ThemeModel.title == title)
            result = await session.execute(q)
            theme = result.scalars().first()
            if theme:
                return theme.convert_to_dc()

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        async with self.app.database.session() as session:
            q = select(ThemeModel).where(ThemeModel.id == id_)
            result = await session.execute(q)
            theme = result.scalars().first()
            if theme:
                return theme.convert_to_dc()

    async def list_themes(self) -> list[Theme]:
        async with self.app.database.session() as session:
            q = select(ThemeModel)
            result = await session.execute(q)
            themes = result.scalars().all()
            return [theme.convert_to_dc() for theme in themes]

    async def create_answers(self, question_id: int, answers: list[Answer]) -> list[Answer]:
        pass

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        async with self.app.database.session() as session:
            answers = [AnswerModel(title=answer.title, is_correct=answer.is_correct) for answer in answers]
            question = QuestionModel(title=title, theme_id=theme_id, answers=answers)
            session.add(question)
            await session.commit()
            return question.convert_to_dc()

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        async with self.app.database.session() as session:
            q = select(QuestionModel).where(QuestionModel.title == title).options(selectinload(QuestionModel.answers))
            result = await session.execute(q)
            question = result.scalars().first()
            if question:
                return question.convert_to_dc()

    async def list_questions(self, theme_id: Optional[int] = None) -> list[Question]:
        async with self.app.database.session() as session:
            if theme_id:
                q = select(QuestionModel).where(QuestionModel.theme_id == theme_id)
            else:
                q = select(QuestionModel)
            result = await session.execute(q.options(selectinload(QuestionModel.answers)))
            questions = result.scalars().all()
            return [q.convert_to_dc() for q in questions]
