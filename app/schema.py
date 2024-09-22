from datetime import datetime
from typing import Literal
from pydantic import BaseModel


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


class DeleteAdvertisementsResponse(StatusSuccessBase):
    pass