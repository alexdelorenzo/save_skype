#!/usr/bin/python3

from collections import namedtuple, defaultdict
from os import getcwd, chdir
from sqlite3 import connect
from types import GeneratorType

try:
    import click

except ImportError as ex:
    raise ImportError("Please install click via pip") from ex


# Filename params
MAX_NAME_LEN = 60
CHAT_FMT = "chat_%s_%s"
EXT = ".txt"

# SQL statements
COL_SQL = "PRAGMA table_info(Messages);"  # grabs column names 
MSG_SQL = "select * from Messages;"


class Message(namedtuple('Message', 'user msg')):
    def __str__(self):
        return '%s: %s' % (str(self.user), str(self.msg))


class Chat(namedtuple('Chat', 'users msgs id')):
    def __new__(cls, msgs: tuple, id: int=None):
        users = sorted({msg.user for msg in msgs})

        return super().__new__(cls, users, msgs, id)

    def __str__(self):
        return '\n'.join(map(str, self))

    def __repr__(self):
        chat_id = self.id if self.id else '?'
        msgs = len(self.msgs)
        users = ', '.join(self.users)

        return "<Chat #%s with %s messages by %s>" % (chat_id, msgs, users)

    def __hash__(self):
        return hash(str(self)) if self.id is None else self.id

    def __iter__(self):
        return iter(self.msgs)

    def save(self, filename: str=None, max_length: int=MAX_NAME_LEN) -> str:
        users = '_'.join(self.users)

        if not filename:
            filename = CHAT_FMT % (hash(self), users)

        filename = filename[:max_length] + EXT
        
        with open(filename, 'w') as file:
            file.write(str(self))

        return filename


def get_skype_map(path: str) -> defaultdict:
    with connect(path) as connection:
        cursor = connection.cursor()
        col_info = cursor.execute(COL_SQL)
        fields = [info[1] for info in col_info.fetchall()]
        rows = cursor.execute(MSG_SQL).fetchall()
    
    # TODO: just write the SQL that makes all of this unnecessary
    Row = namedtuple("Row", fields)
    skype_map = defaultdict(list)

    for row in rows:
        row = Row(*row)
        skype_map[row.convo_id].append(row)

    return skype_map

def gen_skype_chats(path: str) -> GeneratorType:
    skype_map = get_skype_map(path)

    for chat_id, msgs in skype_map.items():
        msg_objs = tuple(Message(row.author, row.body_xml) 
                         for row in msgs)

        yield Chat(msg_objs, chat_id)

@click.command()
@click.option("-s", "--save", default='.', help="Path to save chats")
@click.argument("file")
def chats_to_files(file: str=None, save: str='.'):
    if not file:
        raise OSError("Skype main.db location not supplied.")

    cwd = getcwd()
    chdir(save)

    for count, chat in enumerate(gen_skype_chats(file)):
        print(chat.save())

    print("%s files saved to %s" % (count + 1, save))

    chdir(cwd)


if __name__ == "__main__":
    chats_to_files()
