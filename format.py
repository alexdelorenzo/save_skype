from html_wrapper import HtmlWrapper


def fmt_duration(sec: HtmlWrapper) -> str:
    if sec is None:
        return '0s'

    sec = int(str(sec))

    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)

    h_str = ('%sh' % h) if h else ''
    m_str = ('%sm' % m) if m else ''
    s_str = ('%ss' % s) if s else ''

    return ' '.join(string for string in (h_str, m_str, s_str) if string)


def get_duration_str(part: HtmlWrapper) -> str:
    return "%s's call duration %s." % (part['identity'], fmt_duration(part.duration))


def format_msg(msg: str) -> str:
    if msg is None:
        return msg

    if '</' in msg:
        wrapped = HtmlWrapper(msg)
        part_tags = wrapped.find_all('part')

        if part_tags:
            return '\n'.join(map(get_duration_str, part_tags))

        return wrapped.text.strip()

    return msg
