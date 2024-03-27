from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo:
    def __init__(self, session):
        self.session: AsyncSession = session

    async def execute_mappings_fetchone(self, stmt) -> dict | None:
        data = (await self.session.execute(stmt)).mappings().fetchone()
        if data is not None:
            return dict(**data)

    async def execute_mappings_fetchall(self, stmt) -> list[dict]:
        ds = (await self.session.execute(stmt)).mappings().fetchall()
        return [dict(**d) for d in ds]
