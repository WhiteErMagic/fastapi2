from sqlalchemy.ext.asyncio import AsyncSession
from models import ORM_OBJECT, ORM_CLS
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


async def add_item(session: AsyncSession, item: ORM_OBJECT) -> ORM_OBJECT:
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as err:
        if err.orig.pgcode == '23505':
            raise HTTPException(status_code=409, detail='Item already exist')
        raise err
    return item


async def get_item(session: AsyncSession, orm_cls: ORM_CLS, id: int) -> ORM_OBJECT:
    orm_obj = await session.get(orm_cls, id)
    if orm_obj is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return orm_obj


async def delete_item(session: AsyncSession, orm_cls: ORM_CLS, id: int) -> None:
    orm_obj = await session.get(session, orm_cls, id)
    await session.delete(orm_obj)