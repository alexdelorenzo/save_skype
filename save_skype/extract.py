#!/usr/bin/env python3

from collections import namedtuple, defaultdict
from datetime import datetime
from os import getcwd, chdir
from sqlite3 import connect
from types import GeneratorType

from .save_skype.format_msg import format_msg

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


class Message(namedtuple('Message', 'timestamp user msg')):
    def __str__(self):
        dt = datetime.fromtimestamp(self.timestamp)

        return MSG_FMT % (str(dt), str(self.user), str(self.formatted_msg))

    @property
    def formatted_msg(self) -> str:
        return format_msg(self.msg)


class Chat(namedtuple('Chat', 'users msgs id')):
    def __new__(cls, msgs: tuple, id: int=None):
        users = sorted({msg.user for msg in msgs})

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

    def save(self, filename: str=None, max_length: int=MAX_NAME_LEN) -> str:
        users = '_'.join(self.users)

        if not filename:
            filename = CHAT_FILENAME_FMT % (hash(self), users)

        filename = filename[:max_length] + EXT

        with open(filename, 'w') as file:
            file.write(str(self))

        return filename


def gen_rows(path: str) -> GeneratorType:
    with connect(path) as connection:
        cursor = connection.cursor()
        col_info = cursor.execute(COL_SQL)
        fields = [info[1] for info in col_info.fetchall()]
        rows = cursor.execute(MSG_SQL).fetchall()

    Row = namedtuple("Row", fields)

    for row in rows:
        yield Row(*row)


def get_skype_map(path: str) -> defaultdict:
    # TODO: just write the SQL that makes all of this unnecessary
    row_gen = gen_rows(path)
    skype_map = defaultdict(list)

    for row in row_gen:
        skype_map[row.convo_id].append(row)

    return skype_map


def gen_skype_chats(path: str) -> GeneratorType:
    skype_map = get_skype_map(path)

    for chat_id, msgs in skype_map.items():
        msg_objs = tuple(Message(row.timestamp, row.author, format_msg(row.body_xml))
                         for row in msgs)

        yield Chat(msg_objs, chat_id)


@click.command()
@click.option("-s", "--save", default='.', help="Path to save chats")
@click.argument("file")
def chats_to_files(file: str=None, save: str='.'):
    if not file:
        raise OSError("Skype main.db location not supplied.")

    cwd = getcwd()

    # ALWAYS go back to the current working dir
    try:
        chdir(save)

        file_count = 0
        for file_count, chat in enumerate(gen_skype_chats(file), start=1):
            print(chat.save())

        print("%s files saved to %s" % (file_count, save))

    finally:
        chdir(cwd)


if __name__ == "__main__":
    chats_to_files()
