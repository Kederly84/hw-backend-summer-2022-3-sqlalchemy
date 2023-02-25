from aiohttp.web_exceptions import HTTPNotFound, HTTPBadRequest, HTTPConflict
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title = self.data["title"]
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict
        raw_theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(raw_theme))


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data['title']
        answers = self.data['answers']
        theme_id = self.data['theme_id']
        existing_themes = await self.store.quizzes.list_themes()
        if not theme_id or not existing_themes:
            raise HTTPNotFound
        if len(answers) < 2:
            raise HTTPBadRequest
        flag = False
        counter = 0
        for ans in answers:
            if ans['is_correct']:
                flag = True
                counter += 1
        if flag is False or counter != 1:
            raise HTTPBadRequest
        answers = [Answer(title=ans['title'], is_correct=ans['is_correct']) for ans in answers]
        question = await self.store.quizzes.create_question(title=title, theme_id=theme_id, answers=answers)
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        result = await self.store.quizzes.list_questions()
        print("Next step", result)
        for r in result:
            print(r.title)
        return json_response(data=ListQuestionSchema().dump({"questions": result}))


class QuestionByTitle(AuthRequiredMixin, View):

    @response_schema(ListQuestionSchema)
    async def post(self):
        title = self.data['title']
        result = await self.store.quizzes.get_question_by_title(title=title)
        return json_response(data=ListQuestionSchema().dump({"questions": result}))
