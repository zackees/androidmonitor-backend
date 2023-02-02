"""
Database.
"""

from datetime import datetime
from typing import Any, Sequence
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine, DateTime, Row
from sqlalchemy.orm import sessionmaker
from androidmonitor_backend.settings import DB_URL


engine = create_engine(DB_URL)
meta = MetaData()
uuid_table = Table(
    "uuid",
    meta,
    Column("id", Integer, primary_key=True),
    Column("uuid", String),
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


def db_get_recent(limit=10) -> Sequence[Row[Any]]:
    """Get the uuids."""
    db_init_once()
    with engine.connect() as conn:
        select = uuid_table.select().where().order_by(uuid_table.c.created.desc()).limit(limit)
        result = conn.execute(select)
        rows = result.fetchall()
        return rows


def db_insert_uuid(uuid: str, created: datetime) -> None:
    """Insert a uuid."""
    db_init_once()
    with Session() as session:
        insert = uuid_table.insert().values(uuid=uuid, created=created)
        session.execute(insert)
        session.commit()
