import bcrypt
import fastapi
import pydantic
from fastapi import Depends, HTTPException
from fastapi_filter import FilterDepends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from lifespan import lifespan
import schema
from dependencies import SessionDependency, TokenDependency
import crud
import models
from constants import STATUS_SUCCESS_RESPONSE
from config import DEFAULT_ROLE
from models import Right, Token, Role, User


app = fastapi.FastAPI(
    title='MyApp',
    version='0.0.1',
    description='...',
    lifespan=lifespan
)


@app.get('/advertisements/{id}', response_model=schema.GetAdvertisementsResponse)
async def get_advertisement(id: int, session: SessionDependency):
    advertisement = await get_advertisement(session, models.Advertisements, id)
    return advertisement.dict


@app.post('/advertisements/', response_model=schema.CreateAdvertisementsResponse)
async def post_advertisement(json: schema.CreateAdvertisementsRequest, session: SessionDependency, token: Token):
    advertisement = models.Advertisements(**json.model_dump())
    await check_access_rights(session, token, models.Advertisements, write=True, read=False, raise_exception=True)
    advertisement = await crud.add_item(session, advertisement)
    return advertisement.id


@app.patch('/advertisements/{id}', response_model=schema.UpdateAdvertisementsResponse)
async def patch_advertisement(id: int, json: schema.CreateAdvertisementsRequest, session: SessionDependency):
    advertisement = await crud.get_item(session, models.Advertisements, id)
    await crud.add_item(session, advertisement)
    return advertisement.id


@app.delete('/advertisements/{id}', response_model=schema.DeleteAdvertisementsResponse)
async def delete_advertisement(id: int, session: SessionDependency):
    advertisement = await crud.get_item(session, models.Advertisements, id)
    await delete_advertisement(advertisement)
    return {STATUS_SUCCESS_RESPONSE}


@app.get('/advertisements?title=titlestr}', response_model=schema.GetAdvertisementsResponse)
async def get_product(session: SessionDependency, filter: schema.AdvertisementsFilter = FilterDepends(schema.AdvertisementsFilter)) -> list:
    query_filter = filter.filter(select(models.Advertisements))
    return session.exec(query_filter).all()


@app.post('/user', response_model=schema.CreateUserResponse)
async def create_user(user_data: schema.CreateUserRequest, session: SessionDependency):
    user = models.User(**user_data.dict())
    password = user_data.password.encode()
    user.password = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
    query = select(models.Role).where(Role.name==DEFAULT_ROLE)
    role = await session.scalar(query)
    user.roles = [role]
    await crud.add_item(session, user)
    return user.id_dict


@app.post('/login', response_model=schema.LoginResponse)
async def login(login_data: schema.LoginResponse, session: SessionDependency):
    user_query = select(models.User).where(models.User.name == login.name)
    user_model = await session.scalar(user_query)
    if user_model is None:
        raise fastapi.HTTPException(401, 'User or password is incorrect')
    token = models.Advertisements(user_id = user_model.id)
    token = await crud.add_item(session, token)
    return {'token': token.token}


@app.patch('/user/{id}', response_model=schema.UpdateUserResponse)
async def patch_user(id: int, json: schema.CreateUserResponse, session: SessionDependency):
    user = await crud.get_item(session, models.User, id)
    await crud.add_item(session, user)
    return user.id


@app.get('/user/{id}', response_model=schema.GetUserResponse)
async def get_user(id: int, session: SessionDependency):
    user = await get_advertisement(session, models.User, id)
    return user.dict


@app.delete('/user/{id}', response_model=schema.DeleteUserResponse)
async def delete_user(id: int, session: SessionDependency):
    user = await crud.get_item(session, models.User, id)
    await delete_advertisement(user)
    return {STATUS_SUCCESS_RESPONSE}


async def check_access_rights(
        session: AsyncSession,
        token: Token,
        model: models.ORM_CLS | models.ORM_OBJECT,
        write: bool,
        read: bool,
        owner_field: str = 'user_id',
        raise_exception: bool = True
) -> bool:
    user = token.user
    where_args = [models.User.id == Token.user_id, Right.model == model._model]
    if write:
        where_args.append(Right.write == True)
    if read:
        where_args.append(Right.read == True)
    if (hasattr(model, owner_field)) and getattr(model, owner_field) != token.user_id:
        where_args.append(Right.only_own == False)

    right_query = select(
        func.count(User.id)).join(Role, User.roles).join(Right, Role.rights).where(*where_args)

    rights_count = await session.scalar(right_query)
    if not rights_count and raise_exception:
        raise HTTPException(403, detail="access denied")
    return rights_count > 0

