from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session, get_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data["email"]
        admin = await self.store.admins.get_by_email(email)
        if not admin:
            raise HTTPForbidden
        pwd = self.data["password"]
        if not admin.is_password_valid(pwd):
            raise HTTPUnauthorized
        session = await new_session(self.request)
        session['admin'] = {'id': admin.id, 'email': admin.email}
        admin_resp = {
                "id": admin.id,
                "email": admin.email,
            }
        return json_response(data=admin_resp)


class AdminCurrentView(View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        session = await get_session(self.request)
        if not self.request.cookies.get('AIOHTTP_SESSION') and not session.get('admin'):
            raise HTTPForbidden
        if not session.get('admin'):
            raise HTTPUnauthorized
        raw_admin = {'id': session['admin']['id'], 'email': session['admin']['email']}
        return json_response(data=raw_admin)
