from sqlalchemy.ext.asyncio import async_sessionmaker


class UnitOfWork:
    def __init__(self, session_maker):
        self.session_maker: async_sessionmaker = session_maker

    async def __aenter__(self):
        self.session = self.session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        await self.session.commit()
        await self.session.close()
