try:
    from html_wrapper import HtmlWrapper

except ImportError as ex:
    raise ImportError("Please install html_wrapper via pip3") from ex


SEC_IN_MIN = 60
MIN_IN_HR = 60
NO_MSG_CONTENT = "<NO_MESSAGE_CONTENT>"


def fmt_duration(sec: HtmlWrapper) -> str:
    if sec is None:
        return '0s'

    sec = int(str(sec))

    m, s = divmod(sec, SEC_IN_MIN)
    h, m = divmod(m, MIN_IN_HR)

    h_str = ('%sh' % h) if h else ''
    m_str = ('%sm' % m) if m else ''
    s_str = ('%ss' % s) if s else ''

    return ' '.join(string for string in (h_str, m_str, s_str) if string)


def get_duration_str(part: HtmlWrapper) -> str:
    return "%s's call duration %s." % (part['identity'], fmt_duration(part.duration))


def format_msg(msg: str) -> str:
    if msg is None:
        return NO_MSG_CONTENT

    if '</' in msg:
        wrapped = HtmlWrapper(msg)
        part_tags = wrapped.find_all('part')  # part tags hold call info

        if part_tags:
            return ' '.join(map(get_duration_str, part_tags))

        return wrapped.text.strip()

    return msg
