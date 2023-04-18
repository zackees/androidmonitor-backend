"""
Database.
"""

# pylint: disable=redefined-builtin,line-too-long

import random
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Sequence

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import backref, relationship, sessionmaker

from androidmonitor_backend.log import make_logger
from androidmonitor_backend.settings import DB_URL, IS_TEST


class DuplicateError(Exception):
    """Duplicate error."""

    pass  # pylint: disable=unnecessary-pass


log = make_logger(__name__)

engine = create_engine(DB_URL)
meta = MetaData()
user_table = Table(
    "user",
    meta,
    Column("uid", String, primary_key=True),
    Column("created", DateTime(timezone=True), index=True),
    Column("token", String, index=True),
    Column("version", String, default="0.2"),  # beta, pre-release.
)
vid_table = Table(
    "videos",
    meta,
    # Foreign key to uid_table
    Column("id", Integer, primary_key=True),
    Column("user_uid", String),
    Column("uri_video", String),
    Column("appname", String),
    Column("start", DateTime(timezone=True)),
    Column("end", DateTime(timezone=True)),
    Column("uri_meta", String),
    Column("created", DateTime(timezone=True), index=True),
)
logs_table = Table(
    "logs",
    meta,
    # Foreign key to uid_table
    Column("id", Integer, primary_key=True),
    Column("user_uid", String),
    Column("log", String),
    Column("created", DateTime(timezone=True), index=True),
)

# Define a relationship between the user and videos tables
videos_relationship = relationship(
    "video_relationship",
    backref=backref("user", uselist=False),
    primaryjoin=user_table.c.uid == vid_table.c.user_uid,
)

# Define a relationship between the user and logs tables
logs_relationship = relationship(
    "log_relationship",
    backref=backref("user", uselist=False),
    primaryjoin=user_table.c.uid == logs_table.c.user_uid,
)


Session = sessionmaker(bind=engine)


@dataclass
class VideoItem:
    """Video item."""

    id: int
    uid: str
    uri_video: str
    uri_meta: str
    created: datetime


def db_init_once() -> None:
    """Initialize the database."""
    data = db_init_once.__dict__
    if "init" in data:
        return
    meta.create_all(engine)
    data["init"] = True


def db_add_log(uid: str, log_str: str) -> None:
    """Add a log."""
    db_init_once()
    with Session() as session:
        insert = logs_table.insert().values(
            user_uid=uid,
            log=log_str,
            created=datetime.utcnow(),
        )
        session.execute(insert)
        session.commit()


def db_list_logs(uid: str, limit: int = 10) -> list[tuple[int, datetime]]:
    """List the logs."""
    db_init_once()
    out: list[tuple[int, datetime]] = []
    with Session() as session:
        select = (
            logs_table.select()
            .where(logs_table.c.user_uid == uid)
            .order_by(logs_table.c.created.desc())
            .limit(limit)
        )
        result = session.execute(select)
        for row in result.fetchall():
            id = row.id  # type: ignore
            created = row.created
            out.append((id, created))
    return out


def db_get_log(log_id: int) -> tuple[str, datetime]:
    """Get a log."""
    db_init_once()
    with Session() as session:
        select = logs_table.select().where(logs_table.c.id == log_id)
        result = session.execute(select)
        rows = result.fetchall()
        if len(rows) == 0:
            raise ValueError("log_id not found")
        log_str: str = rows[0].log
        created: datetime = rows[0].created
        out: tuple[str, datetime] = (log_str, created)
        return out


def db_register_upload(
    uid: str,
    uri_video: str,
    appname: str,
    start: datetime,
    end: datetime,
    uri_meta: str,
) -> None:
    """Register a video upload."""
    db_init_once()
    with Session() as session:
        select = user_table.select().where(user_table.c.uid == uid)
        result = session.execute(select)
        rows = result.fetchall()
        if len(rows) == 0:
            raise ValueError("uid not found")
        insert = vid_table.insert().values(
            user_uid=uid,
            uri_video=uri_video,
            appname=appname,
            start=start,
            end=end,
            uri_meta=uri_meta,
            created=datetime.utcnow(),
        )
        session.execute(insert)
        session.commit()


def db_list_uploads(uid: str, limit: int = 10) -> Sequence[Row[Any]]:
    """List the uploads."""
    db_init_once()
    with Session() as session:
        select = (
            vid_table.select()
            .where(vid_table.c.user_uid == uid)
            .order_by(vid_table.c.created.desc())
            .limit(limit)
        )
        result = session.execute(select)
        return result.fetchall()


def db_uid_exists(uid: str) -> bool:
    """Check if a uid exists."""
    db_init_once()
    with Session() as session:
        select = user_table.select().where(user_table.c.uid == uid)
        result = session.execute(select)
        rows = result.fetchall()
        return len(rows) > 0


def db_get_user_from_token(token: str) -> Row[Any] | None:
    """Get a uid."""
    db_init_once()
    with Session() as session:
        select = user_table.select().where(user_table.c.token == token)
        result = session.execute(select)
        rows = result.fetchall()
        if len(rows) == 0:
            return None
        return rows[0]


def db_get_user_from_uid(uid: str) -> Row[Any] | None:
    """Get a uid."""
    db_init_once()
    with Session() as session:
        select = user_table.select().where(user_table.c.uid == uid)
        result = session.execute(select)
        rows = result.fetchall()
        if len(rows) == 0:
            return None
        return rows[0]


def db_get_recent(limit=10) -> Sequence[Row[Any]]:
    """Get the uids."""
    return db_get_users(limit=limit)


def db_get_users(
    uidlist: list[str] | None = None,
    limit: int = 100,
    start: datetime | None = None,
    end: datetime | None = None,
) -> Sequence[Row[Any]]:
    """Get the users."""
    db_init_once()
    with Session() as session:
        select = user_table.select()
        if uidlist is not None:
            select = select.where(user_table.c.uid.in_(uidlist))
        if start is not None:
            select = select.where(user_table.c.created >= start)
        if end is not None:
            select = select.where(user_table.c.created <= end)
        select = select.order_by(user_table.c.created.desc()).limit(limit)
        result = session.execute(select)
        rows = result.fetchall()
        return rows


def db_get_video(id: int) -> VideoItem | None:
    """Get the uids."""
    db_init_once()
    with Session() as session:
        select = vid_table.select().where(vid_table.c.id == id)
        result = session.execute(select)
        rows = result.fetchall()
        if len(rows) == 0:
            return None
        row = rows[0]
        try:
            return VideoItem(
                id=row.id,
                uid=row.user_uid,
                uri_video=row.uri_video,
                uri_meta=row.uri_meta,
                created=row.created,
            )
        except Exception as exc:  # pylint: disable=broad-except
            log.exception(exc)
            return None


def db_get_recent_videos(limit=10) -> list[VideoItem]:
    """Get the uids."""
    db_init_once()
    with Session() as session:
        out: list[VideoItem] = []
        select = (
            vid_table.select().where().order_by(vid_table.c.created.desc()).limit(limit)
        )
        result = session.execute(select)
        rows = result.fetchall()
        for row in rows:
            try:
                vid = VideoItem(
                    id=row.id,
                    uid=row.user_uid,
                    uri_video=row.uri_video,
                    uri_meta=row.uri_meta,
                    created=row.created,
                )
                out.append(vid)
            except Exception as exc:  # pylint: disable=broad-except
                log.exception(exc)
    return out


def db_get_recent_logs_ids(limit=10) -> list[int]:
    """Get the recent logs ids."""
    db_init_once()
    with Session() as session:
        out: list[int] = []
        select = (
            logs_table.select()
            .where()
            .order_by(logs_table.c.created.desc())
            .limit(limit)
        )
        result = session.execute(select)
        rows = result.fetchall()
        for row in rows:
            out.append(row.id)
    return out


def db_clear() -> None:
    """Clear the database."""
    db_init_once()
    with engine.connect():
        user_table.drop(engine)
        vid_table.drop(engine)
        logs_table.drop(engine)
        meta.create_all(engine)


def db_to_string() -> str:
    """Convert the database to a string."""
    db_init_once()
    with Session() as session:
        select = user_table.select()
        result = session.execute(select)
        rows = result.fetchall()
        out: list[str] = ["user table"]
        for row in rows:
            out.append(f"{row.uid} {row.created} {row.token}")
        select = vid_table.select()
        result = session.execute(select)
        rows = result.fetchall()
        for row in rows:
            out.append(f"{row.user_uid} {row.uri_video} {row.uri_meta} {row.created}")
        return "\n".join(out)


def db_insert_uid(uid: str, created: datetime) -> None:
    """Insert a uid. Raises an IntegrityError if the uid already exists."""
    db_init_once()
    with Session() as session:
        try:
            insert = user_table.insert().values(uid=uid, created=created)
            session.execute(insert)
            session.commit()
        except IntegrityError as error:
            if "UNIQUE constraint failed" in str(error):
                raise DuplicateError from error
            raise


def db_add_uid() -> tuple[bool, str, str]:
    """Adds a randomly generated UID to the database."""
    while True:
        # generate a random 8 digit number
        random_value = random.randint(0, 99999999)
        rand_str = str(random_value).zfill(8)
        # sum all digits and add the last digit as the checksum
        total = 0
        for char in rand_str:
            total += int(char)
        total = total % 10
        rand_str += str(total)
        # insert a - in the middle
        out_rand_str = rand_str[:3] + "-" + rand_str[3:6] + "-" + rand_str[6:]
        now = datetime.utcnow()
        # add it to the database
        try:
            db_insert_uid(rand_str, datetime.utcnow())
            log.info("Added uid %s", rand_str)
            # does the value already exist
            break
        except DuplicateError:
            continue
    return True, out_rand_str, str(now)


def db_try_register(uid: str) -> tuple[bool, str]:
    """Try to register a device."""
    db_init_once()
    if IS_TEST:
        # Debugging if the uid is already registered. We don't want this
        # to happen in production because it would be a security issue.
        row = db_get_user_from_uid(uid)
        recent_rows = db_get_recent()
        print(recent_rows)
        if row is None:
            log.info("uid %s doesn't exist and might be expired", uid)
            return False, "Error the token doesn't exist"
        if row.token is not None:
            log.info("uid %s already registered", uid)
            return False, "Error the token is already registered"
    token128 = secrets.token_hex(64)  # 2 bytes per char
    with Session() as session:
        # update uid with token
        log.info("Attempting to register uid %s with token %s", uid, token128)
        # update the uid if of the token only if the previous token was None
        # flake8: noqa=E711
        update = (
            user_table.update()
            .where(user_table.c.uid == uid)
            .where(user_table.c.token == None)  # type: ignore # pylint: disable=singleton-comparison
            .values(token=token128)
        )
        result = session.execute(update)
        session.commit()
        if result.rowcount == 0:  # type: ignore
            log.info("uid %s already registered or it doesn't exist", uid)
            return False, ""
        log.info("uid %s registered", uid)
        return True, token128


def db_get_uploads(
    uid: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    appname: str | None = None,
    count: int | None = None,
) -> Sequence[Row[Any]]:
    """Get the uids."""
    db_init_once()
    with Session() as session:
        select = vid_table.select()
        if uid is not None:
            select = select.where(vid_table.c.user_uid == uid)
        if start is not None:
            select = select.where(vid_table.c.start >= start)
        if end is not None:
            select = select.where(vid_table.c.end <= end)
        if appname is not None:
            select = select.where(vid_table.c.appname == appname)
        select = select.order_by(vid_table.c.start.desc())
        if count is not None:
            select = select.limit(count)
        result = session.execute(select)
        rows = result.fetchall()
        return rows


def db_is_client_registered(token: str, uid: str) -> bool:
    """Returns true if the client with the token is registered."""
    db_init_once()
    with Session() as session:
        select = (
            user_table.select()
            .where(user_table.c.uid == uid)
            .where(user_table.c.token == token)
        )
        result = session.execute(select)
        rows = result.fetchall()
        return len(rows) > 0


def db_is_token_valid(token: str) -> bool:
    """Returns true if the token is valid."""
    db_init_once()
    with Session() as session:
        select = user_table.select().where(user_table.c.token == token)
        result = session.execute(select)
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
            user_table.delete()
            .where(user_table.c.created < max_age)
            .where(user_table.c.token == None)  # type: ignore # pylint: disable=singleton-comparison
        )
        session.execute(delete)
        session.commit()
