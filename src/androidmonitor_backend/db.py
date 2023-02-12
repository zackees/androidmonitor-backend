"""
Database.
"""

from datetime import datetime, timedelta
import secrets
from typing import Any, Sequence


from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    Row,
    String,
    Table,
    create_engine,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from androidmonitor_backend.log import make_logger
from androidmonitor_backend.settings import DB_URL


class DuplicateError(Exception):
    """Duplicate error."""

    pass  # pylint: disable=unnecessary-pass


log = make_logger(__name__)

engine = create_engine(DB_URL)
meta = MetaData()
uuid_table = Table(
    "uuid",
    meta,
    Column("id", Integer, primary_key=True),
    Column("uuid", String, unique=True),
    Column("created", DateTime, index=True),
    Column("token", String, index=True),
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


def db_get_uuid(uuid: str) -> Row[Any] | None:
    """Get a uuid."""
    db_init_once()
    with engine.connect() as conn:
        select = uuid_table.select().where(uuid_table.c.uuid == uuid)
        result = conn.execute(select)
        rows = result.fetchall()
        if len(rows) == 0:
            return None
        return rows[0]


def db_get_recent(limit=10) -> Sequence[Row[Any]]:
    """Get the uuids."""
    db_init_once()
    with engine.connect() as conn:
        select = uuid_table.select().where().order_by(uuid_table.c.created.desc()).limit(limit)
        result = conn.execute(select)
        rows = result.fetchall()
        return rows


def db_clear(delete=False) -> None:
    """Clear the database."""
    db_init_once()
    with engine.connect() as conn:
        if delete:
            uuid_table.drop(engine)
            meta.create_all(engine)
        else:
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


def db_try_register(uuid: str) -> tuple[bool, str]:
    """Try to register a device."""
    db_init_once()
    token128 = secrets.token_hex(64)  # 2 bytes per char
    with Session() as session:
        # update uuid with token
        log.info("Attempting to register uid %s with token %s", uuid, token128)
        # update the uid if of the token only if the previous token was None
        # flake8: noqa=E711
        update = (
            uuid_table.update()
            .where(uuid_table.c.uuid == uuid)
            .where(uuid_table.c.token == None)  # type: ignore # pylint: disable=singleton-comparison
            .values(token=token128)
        )
        result = session.execute(update)
        session.commit()
        if result.rowcount == 0:
            log.info("uid %s already registered or it doesn't exist", uuid)
            return False, ""
        log.info("uid %s registered", uuid)
        return True, token128


def db_expire_old_uuids(max_time_seconds: int) -> None:
    """Expire old uuids."""
    db_init_once()
    with Session() as session:
        max_age: datetime = datetime.utcnow() - timedelta(seconds=max_time_seconds)
        # delete old uuids where token is null
        # flake8: noqa=E711
        delete = (
            uuid_table.delete()
            .where(uuid_table.c.created < max_age)
            .where(uuid_table.c.token == None)  # type: ignore # pylint: disable=singleton-comparison
        )
        session.execute(delete)
        session.commit()
