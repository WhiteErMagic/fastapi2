import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from models import Role, Right, Advertisements, User, Session


async def create_default_role(session: AsyncSession):

    rights = []
    for wr in True, False:
        for model in Advertisements, User:
            right = Right(
                model=model._model,
                only_own=True,
                read=wr,
                write=not wr
            )
            rights.append(right)
    role = Role(name='user', rights=rights)
    session.add_all([role, *rights])
    await session.commit()


async def main():
    async with Session() as session:
        await create_default_role(session)


if __name__ == '__main__':
    asyncio.run(main())