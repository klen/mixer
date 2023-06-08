from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID


# Simple classes
# --------------
class CustomType(str):
    pass


class User:
    id: int
    email: str
    role: Literal["user", "admin"]
    logged_at: Optional[datetime] = None


class Post:
    id: UUID
    title: CustomType
    image: bytes
    body: str
    user: User
    order: int = 0
    is_published: bool = False
    dtpublish: date


# Dataclasses
# -----------
from dataclasses import dataclass


@dataclass
class DCUser:
    id: int
    email: str
    role: Literal["user", "admin"]
    logged_at: Optional[datetime] = None


@dataclass
class DCPost:
    id: UUID
    title: CustomType
    image: bytes
    body: str
    user: DCUser
    dtpublish: date
    order: int = 0
    is_published: bool = False


# Peewee ORM
# -------------

import peewee as pw

db = pw.SqliteDatabase(":memory:")


class PWCustomField(pw.CharField):
    pass


class PWUser(pw.Model):
    id = pw.AutoField()
    email = pw.CharField()
    role = pw.CharField(choices=[("user", "user"), ("admin", "admin")])
    logged_at = pw.DateTimeField(null=True)

    class Meta:
        database = db


class PWPost(pw.Model):
    """Peewee model"""

    id = pw.UUIDField(primary_key=True)
    title = PWCustomField()
    image = pw.BlobField()
    body = pw.TextField()
    dtpublish = pw.DateField()
    order = pw.IntegerField(default=0)
    is_published = pw.BooleanField(default=False)
    user = pw.ForeignKeyField(PWUser)

    class Meta:
        database = db


PWUser.create_table()
PWPost.create_table()


# Peewee-AIO models
# -------------

from peewee_aio import AIOModel, Manager
from peewee_aio import fields as pwa_fields

pwa_manager = Manager("aiosqlite:///:memory:")


class PWACustomField(pwa_fields.CharField):
    pass


@pwa_manager.register
class PWAUser(AIOModel):
    id = pwa_fields.AutoField()
    email = pwa_fields.CharField()
    role = pwa_fields.CharField(choices=[("user", "user"), ("admin", "admin")])
    position = pwa_fields.CharField()
    logged_at = pwa_fields.DateTimeField(null=True)


@pwa_manager.register
class PWAPost(AIOModel):
    id = pwa_fields.UUIDField(primary_key=True)
    title = PWCustomField()
    image = pwa_fields.BlobField()
    body = pwa_fields.TextField()
    dt_publish = pwa_fields.DateField()
    order = pwa_fields.IntegerField(default=0)
    is_published = pwa_fields.BooleanField(default=False)
    user = pwa_fields.AIOForeignKeyField(PWAUser)


# Pydantic classes
# ----------------
import pydantic as pd


class PDUser(pd.BaseModel):
    id: int
    email: str
    role: Literal["user", "admin"]
    logged_at: Optional[datetime] = None


class PDPost(pd.BaseModel):
    """Pydantic model"""

    id: UUID
    title: CustomType
    image: bytes
    body: str
    dtpublish: date
    order: int = 0
    is_published: bool = False
    user: PDUser


# Django models
# -------------
from django.apps.registry import apps
from django.conf import settings
from django.db import connection, models

settings.configure(
    INSTALLED_APPS=[],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
)
apps.populate([__name__])


class DJCustomField(models.CharField):
    pass


class DJUser(models.Model):
    email = models.CharField(max_length=255)
    role = models.CharField(choices=[("user", "user"), ("admin", "admin")], max_length=10)
    logged_at = models.DateTimeField(null=True)


class DJPost(models.Model):
    id = models.UUIDField(primary_key=True)
    title = DJCustomField(max_length=255)
    image = models.BinaryField()
    body = models.TextField()
    dtpublish = models.DateField()
    order = models.IntegerField(default=0)  # type: ignore[]
    is_published = models.BooleanField(default=False)  # type: ignore[]
    user = models.ForeignKey(DJUser, on_delete=models.CASCADE)


with connection.schema_editor() as schema_editor:
    schema_editor.create_model(DJUser)
    schema_editor.create_model(DJPost)


# Mongoengine models
# ------------------
import mongoengine as me

me.connect("tests")


class MECustomField(me.StringField):
    pass


class MEUser(me.Document):
    email = me.EmailField(required=True)
    role = me.StringField(choices=(("user", "user"), ("admin", "admin")), required=True)
    logged_at = me.DateTimeField(null=True)


class MEPost(me.Document):
    title = MECustomField(required=True)
    image = me.BinaryField()
    body = me.StringField(required=True)
    dtpublish = me.DateField()
    order = me.IntField(default=0)
    is_published = me.BooleanField(default=False)
    user = me.ReferenceField(MEUser, required=True)


# Marshmallow schemas
# -------------------

import marshmallow as ma


class MACustomField(ma.fields.String):
    pass


class MAUser(ma.Schema):
    email = ma.fields.Email(required=True)
    role = ma.fields.String(
        required=True, validate=ma.validate.OneOf(["user", "admin"])  # type: ignore[]
    )
    logged_at = ma.fields.DateTime(allow_none=True)


class MAPost(ma.Schema):
    id = ma.fields.UUID(required=True)
    title = MACustomField(required=True)
    image = ma.fields.Raw()  # TODO
    body = ma.fields.String(required=True)
    dtpublish = ma.fields.Date()
    order = ma.fields.Integer(load_default=0, dump_default=0)
    is_published = ma.fields.Boolean(load_default=False, dump_default=False)
    user = ma.fields.Nested(MAUser, required=True)


# SQLAlchemy models
# -----------------

import sqlalchemy as sa
from sqlalchemy import orm as saorm

SA_ENGINE = sa.create_engine("sqlite:///:memory:")
SA_SESSION = saorm.Session(SA_ENGINE)


class Base(saorm.DeclarativeBase):
    pass


class CustomField(sa.String):
    pass


class Role(Enum):
    USER = "user"
    ADMIN = "admin"


class SAUser(Base):
    __tablename__ = "users"

    id = saorm.mapped_column(sa.Integer, primary_key=True)
    email = saorm.mapped_column(sa.String, nullable=False)
    role = saorm.mapped_column(sa.Enum(Role), nullable=False)
    logged_at = saorm.mapped_column(sa.DateTime, nullable=True)

    posts = saorm.relationship("SAPost", back_populates="user")


class SAPost(Base):
    __tablename__ = "posts"

    # id = saorm.mapped_column(sa.UUID, primary_key=True)
    id = saorm.mapped_column(sa.Integer, primary_key=True)
    title = saorm.mapped_column(CustomField, nullable=False)
    image = saorm.mapped_column(sa.LargeBinary, nullable=False)
    body = saorm.mapped_column(sa.String, nullable=False)
    dtpublish = saorm.mapped_column(sa.Date, nullable=False)
    order = saorm.mapped_column(sa.Integer, nullable=False, default=0)
    is_published = saorm.mapped_column(sa.Boolean, nullable=False, default=False)
    user_id = saorm.mapped_column(sa.ForeignKey("users.id"), nullable=False)

    user = saorm.relationship("SAUser", back_populates="posts")


Base.metadata.create_all(SA_ENGINE)


# ruff: noqa: E402
