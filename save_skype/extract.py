#!/usr/bin/env python3
from typing import NamedTuple, Dict, DefaultDict, Iterable, \
  List, Tuple, Optional
from collections import namedtuple, defaultdict
from pathlib import Path
from datetime import datetime
from os import getcwd, chdir
from sqlite3 import connect

from save_skype.format_msg import format_msg

try:
    import click

except ImportError as ex:
    raise ImportError("Please install click via pip3") from ex


# Filename params
MAX_NAME_LEN = 60
CHAT_FILENAME_FMT = "chat_%s_%s"
EXT = ".txt"

# SQL statements
COL_SQL = "PRAGMA table_info(Messages);"  # grabs column names
MSG_SQL = "select * from Messages;"

# Format strings
MSG_FMT = "[%s] %s: %s"
CHAT_FMT = "<Chat #%s with %s messages by %s>"
DEFAULT_CHAT_ID = "?"


ChatRows = DefaultDict[int, List['Row']]


class Message(NamedTuple):
    timestamp: str
    user: str
    msg: str

    def __str__(self):
        dt = datetime.fromtimestamp(self.timestamp)

        return MSG_FMT % (str(dt), str(self.user), str(self.formatted_msg))

    @property
    def formatted_msg(self) -> str:
        return format_msg(self.msg)


class Chat(NamedTuple):
    users: Tuple[str]
    msgs: Tuple[Message]
    id: int

    def __new__(cls, msgs: Tuple[Message], id: Optional[int] = None):
        users = tuple(sorted({msg.user for msg in msgs}))

        return super().__new__(cls, users, msgs, id)

    def __str__(self):
        return '\n'.join(map(str, self))

    def __repr__(self):
        chat_id = DEFAULT_CHAT_ID if self.id is None else self.id
        msgs = len(self.msgs)
        users = ', '.join(self.users)

        return CHAT_FMT % (chat_id, msgs, users)

    def __hash__(self):
        return hash(str(self)) if self.id is None else self.id

    def __iter__(self):
        return iter(self.msgs)

    def save(self, filename: Optional[str] = None, max_length: int = MAX_NAME_LEN) -> Path:
        users = '_'.join(self.users)

        if not filename:
            filename = CHAT_FILENAME_FMT % (hash(self), users)

        filename = filename[:max_length] + EXT
        path = Path(filename)
        path.write_text(str(self))

        return path.absolute()


def gen_rows(path: Path) -> Iterable['Row']:
    with connect(str(path)) as connection:
        cursor = connection.cursor()
        col_info = cursor.execute(COL_SQL)
        fields = [info[1] for info in col_info.fetchall()]
        rows = cursor.execute(MSG_SQL).fetchall()

    Row = namedtuple("Row", fields)

    for row in rows:
        yield Row(*row)


def get_chat_rows(path: Path) -> ChatRows
    # TODO: just write the SQL that makes all of this unnecessary
    row_gen = gen_rows(path)
    chat_rows = defaultdict(list)

    for row in row_gen:
        chat_rows[row.convo_id].append(row)

    return chat_rows


def get_msg(row: 'Row') -> Message:
    msg = format_msg(row.body_xml)

    return Message(row.timestamp, row.author, msg)


def gen_skype_chats(path: Path) -> Iterable[Chat]:
    chat_rows = get_chat_rows(path)

    for chat_id, rows in chat_rows.items():
        msgs = tuple(map(get_msg, rows))

        yield Chat(msgs, chat_id)


@click.command()
@click.option("-s", "--save", default='.', help="Path to save chats")
@click.argument("file")
def chats_to_files(file: Optional[str] = None, save: str = '.'):
    if not file:
        raise OSError("Skype main.db location not supplied.")

    path = Path(file)
    cwd = getcwd()

    # always go back to the current working dir
    try:
        chdir(save)

        file_count = 0
        chats = gen_skype_chats(path)

        for file_count, chat in enumerate(chats, start=1):
            print(chat.save())

        print(f"{file_count} files saved to {save}")

    finally:
        chdir(cwd)


if __name__ == "__main__":
    chats_to_files()
