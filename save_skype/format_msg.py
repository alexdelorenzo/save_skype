from typing import Optional

try:
    from html_wrapper import HtmlWrapper

except ImportError as ex:
    raise ImportError("Please install html_wrapper via pip3") from ex


SEC_IN_MIN = 60
MIN_IN_HR = 60
NO_MSG_CONTENT = "<NO_MESSAGE_CONTENT>"
UNITS = 'hms'

def fmt_duration(sec: Optional[HtmlWrapper]) -> str:
    if sec is None:
        return '0s'

    sec = int(str(sec))

    m, s = divmod(sec, SEC_IN_MIN)
    h, m = divmod(m, MIN_IN_HR)
    times = h, m, s

    strs = (
        f'{time}{unit}'
        for time, unit in zip(times, UNITS)
        if time
    )

    return ' '.join(strs)


def get_duration_str(part: Optional[HtmlWrapper]) -> str:
    ident = part['identity']
    duration = fmt_duration(part.duration)

    return f"{ident}'s call duration {duration}."


def format_msg(msg: str) -> str:
    if msg is None:
        return NO_MSG_CONTENT

    if '</' in msg:
        wrapped = HtmlWrapper(msg)
        part_tags = wrapped.find_all('part')  # part tags hold call info

        if part_tags:
            calls = map(get_duration_str, part_tags)
            return ' '.join(calls)

        return wrapped.text.strip()

    return msg
