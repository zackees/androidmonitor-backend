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
uid_table = Table(
    "uid",
    meta,
    Column("id", Integer, primary_key=True),
    Column("uid", String, unique=True),
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


def db_uid_exists(uid: str) -> bool:
    """Check if a uid exists."""
    db_init_once()
    with engine.connect() as conn:
        select = uid_table.select().where(uid_table.c.uid == uid)
        result = conn.execute(select)
        rows = result.fetchall()
        return len(rows) > 0


def db_get_uid(uid: str) -> Row[Any] | None:
    """Get a uid."""
    db_init_once()
    with engine.connect() as conn:
        select = uid_table.select().where(uid_table.c.uid == uid)
        result = conn.execute(select)
        rows = result.fetchall()
        if len(rows) == 0:
            return None
        return rows[0]


def db_get_recent(limit=10) -> Sequence[Row[Any]]:
    """Get the uids."""
    db_init_once()
    with engine.connect() as conn:
        select = (
            uid_table.select().where().order_by(uid_table.c.created.desc()).limit(limit)
        )
        result = conn.execute(select)
        rows = result.fetchall()
        return rows


def db_clear(delete=False) -> None:
    """Clear the database."""
    db_init_once()
    with engine.connect() as conn:
        if delete:
            uid_table.drop(engine)
            meta.create_all(engine)
        else:
            conn.execute(uid_table.delete())
            conn.commit()


def db_insert_uid(uid: str, created: datetime) -> None:
    """Insert a uid. Raises an IntegrityError if the uid already exists."""
    db_init_once()
    with Session() as session:
        try:
            insert = uid_table.insert().values(uid=uid, created=created)
            session.execute(insert)
            session.commit()
        except IntegrityError as error:
            if "UNIQUE constraint failed" in str(error):
                raise DuplicateError from error
            raise


def db_try_register(uid: str) -> tuple[bool, str]:
    """Try to register a device."""
    db_init_once()
    token128 = secrets.token_hex(64)  # 2 bytes per char
    with Session() as session:
        # update uid with token
        log.info("Attempting to register uid %s with token %s", uid, token128)
        # update the uid if of the token only if the previous token was None
        # flake8: noqa=E711
        update = (
            uid_table.update()
            .where(uid_table.c.uid == uid)
            .where(uid_table.c.token == None)  # type: ignore # pylint: disable=singleton-comparison
            .values(token=token128)
        )
        result = session.execute(update)
        session.commit()
        if result.rowcount == 0:  # type: ignore
            log.info("uid %s already registered or it doesn't exist", uid)
            return False, ""
        log.info("uid %s registered", uid)
        return True, token128


def db_is_client_registered(uid: str, token: str) -> bool:
    """Returns true if the client with the token is registered."""
    db_init_once()
    with engine.connect() as conn:
        select = (
            uid_table.select()
            .where(uid_table.c.uid == uid)
            .where(uid_table.c.token == token)
        )
        result = conn.execute(select)
        rows = result.fetchall()
        return len(rows) > 0


def db_expire_old_uids(max_time_seconds: int) -> None:
    """Expire old uids."""
    db_init_once()
    with Session() as session:
        max_age: datetime = datetime.utcnow() - timedelta(seconds=max_time_seconds)
        # delete old uids where token is null
        # flake8: noqa=E711
        delete = (
            uid_table.delete()
            .where(uid_table.c.created < max_age)
            .where(uid_table.c.token == None)  # type: ignore # pylint: disable=singleton-comparison
        )
        session.execute(delete)
        session.commit()
