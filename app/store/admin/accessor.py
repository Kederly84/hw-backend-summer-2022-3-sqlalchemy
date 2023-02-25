import typing
from hashlib import sha256


from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):

    async def connect(self, app: "Application"):
        await self.create_admin(email=self.app.config.admin.email, password=self.app.config.admin.password)

    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session() as connection:
            result = await connection.execute(
                select(AdminModel).where(AdminModel.email == email)
            )
            obj: AdminModel | None = result.scalar()
            if obj is not None:
                return obj.convert_to_dc()

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = AdminModel(email=email, password=sha256(password.encode('utf-8')).hexdigest())
        if email:
            async with self.app.database.session() as connection:
                exist_admin = await connection.execute(
                    select(AdminModel).where(AdminModel.email == email)
                )
                exist_admin = exist_admin.scalar()
                print("Here We ARE", exist_admin)
                if not exist_admin:
                    connection.add(admin)
                    await connection.commit()
                    return admin.convert_to_dc()

