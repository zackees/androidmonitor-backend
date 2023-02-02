"""
Database.
"""

from datetime import datetime
from typing import Any, Sequence
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    MetaData,
    create_engine,
    DateTime,
    Row,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from androidmonitor_backend.settings import DB_URL


class DuplicateError(Exception):
    """Duplicate error."""

    pass  # pylint: disable=unnecessary-pass


engine = create_engine(DB_URL)
meta = MetaData()
uuid_table = Table(
    "uuid",
    meta,
    Column("id", Integer, primary_key=True),
    Column("uuid", String, unique=True),
    Column("created", DateTime),
)
Session = sessionmaker(bind=engine)


def db_init_once() -> None:
    """Initialize the database."""
    data = db_init_once.__dict__
    if "init" in data:
        return
    meta.create_all(engine)
    data["init"] = True


def db_uuid_exists(uuid: str) -> bool:
    """Check if a uuid exists."""
    db_init_once()
    with engine.connect() as conn:
        select = uuid_table.select().where(uuid_table.c.uuid == uuid)
        result = conn.execute(select)
        rows = result.fetchall()
        return len(rows) > 0


def db_get_recent(limit=10) -> Sequence[Row[Any]]:
    """Get the uuids."""
    db_init_once()
    with engine.connect() as conn:
        select = (
            uuid_table.select()
            .where()
            .order_by(uuid_table.c.created.desc())
            .limit(limit)
        )
        result = conn.execute(select)
        rows = result.fetchall()
        return rows


def db_clear() -> None:
    """Clear the database."""
    db_init_once()
    with engine.connect() as conn:
        conn.execute(uuid_table.delete())
        conn.commit()


def db_insert_uuid(uuid: str, created: datetime) -> None:
    """Insert a uuid. Raises an IntegrityError if the uuid already exists."""
    db_init_once()
    with Session() as session:
        try:
            insert = uuid_table.insert().values(uuid=uuid, created=created)
            session.execute(insert)
            session.commit()
        except IntegrityError as error:
            if "UNIQUE constraint failed" in str(error):
                raise DuplicateError from error
            raise
