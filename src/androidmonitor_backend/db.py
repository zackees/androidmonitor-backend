"""
Database.
"""

from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine, DateTime
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
meta.create_all(engine)
