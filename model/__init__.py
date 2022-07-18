from pydantic.schema import datetime
from typing import Optional

from sqlmodel import create_engine, Field, SQLModel

POSTGRES_URI = "postgresql://postgres:postgres@0.0.0.0:5432/postgres"


class StarlinkRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creation_date: datetime = Field(index=True)
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    satellite_id: str = Field(index=True)


engine = create_engine(POSTGRES_URI)


def create_table():
    SQLModel.metadata.create_all(engine)
