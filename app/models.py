import datetime
import os
import uuid
from msilib import Table
from typing import Literal, List

from sqlalchemy import create_engine, Integer, String, DateTime, func, ForeignKey, Boolean, Column, UniqueConstraint, \
    CheckConstraint
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped, relationship

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '1234')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'flask_db')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')


PG_DSN = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


role_rights = Table('role_rights_relation', Base.metadata,
                    Column('role_id', ForeignKey('role.id'), index=True),
                    Column('right_id', ForeignKey('right.id'), index=True),
                    )


user_roles = Table('role_roles_relation', Base.metadata,
                   Column('user_id', ForeignKey('advertisements_user.id'), index=True),
                   Column('role_id', ForeignKey('role.id'), index=True),
                   )


class User(Base):
    __tablename__ = 'user'
    _model = "User"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(72), nullable=False)
    registration_time: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    tokens: Mapped[list['Token']] = relationship('token', lazy='joined', back_populates='tokens')
    advertisements: Mapped[Advertisements] = relationship(Advertisements, lazy='jpined', back_populates='user')
    roles: Mapped[list['Role']] = relationship(Role, secondary=user_roles, lazy='joined')

    @property
    def dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Token(Base):
    __tablename__ = 'token'
    _model = "Token"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(func.gen_random_uuid(), unique=True)
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped[User] = relationship(User, back_populates='token', lazy='joined')

    @property
    def dict(self):
        return {
            'id': self.id,
            'token': str(self.token),
            'user_id': self.user_id,
            'creation_time': self.creation_time.isoformat()
        }


class Advertisements(Base):
    __tablename__ = 'advertisements'
    _model = "Advertisements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(1000))
    price: Mapped[int] = mapped_column(Integer)
    date_create: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship('User', lazy='joined', back_populates='advertisements')

    @property
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'date_create': self.date_create.isoformat(),
            'user': self.user
        }


ModelName = Literal['User', 'Advertisements', 'Role', 'Right']


class Right(Base):
    __tablename__ = 'right'
    _model = "Right"
    id: Mapped[int] = mapped_column(primary_key=True)
    write: Mapped[bool] = mapped_column(Boolean, default=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    only_own: Mapped[bool] = mapped_column(Boolean, default=True)
    model: Mapped[ModelName] = mapped_column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('model', 'only_own', 'read', 'write'),
        CheckConstraint('model in ("User", "Advertisements", "Role", "Right")')
    )


class Role(Base):
    __tablename__ = 'role'
    _model = "Role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    rights: Mapped[List[Right]] = relationship(secondary=role_rights, lazy='joined')



ORM_OBJECT = Advertisements | User | Token
ORM_CLS = type[Advertisements] | type[User] | type[Token]
