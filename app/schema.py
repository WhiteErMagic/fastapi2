from datetime import datetime
from typing import Literal, Optional
import uuid
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field

from models import Advertisements


class IdReturnBase(BaseModel):
    id: int


class StatusSuccessBase(BaseModel):
    status: Literal['success']


class GetAdvertisementsResponse(BaseModel):

    id: int
    title: str
    description: str
    price: int
    user: int


class GetUserResponse(BaseModel):

    id: int
    name: str


class CreateAdvertisementsRequest(BaseModel):
    title: str
    description: str
    price: int
    user: int


class CreateAdvertisementsResponse(IdReturnBase):
    pass


class UpdateAdvertisementsRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None


class UpdateAdvertisementsResponse(IdReturnBase):
    pass


class UpdateUserResponse(IdReturnBase):
    pass


class DeleteAdvertisementsResponse(StatusSuccessBase):
    pass


class DeleteUserResponse(StatusSuccessBase):
    pass


class AdvertisementsFilter(Filter):
    title__in: Optional[list[str]] = Field(alias="titlestr")

    class Constants(Filter.Constants):
        model = Advertisements

    class Config:
        allow_population_by_field_name = True


class LoginReuest(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    token: uuid.UUID


class CreateUserRequest(BaseModel):
    login: str
    password: str


class CreateUserResponse(IdReturnBase):
    pass