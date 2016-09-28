from functools import lru_cache

from lxml.html import HtmlElement, fromstring
from lxml.etree import XPath


BS4_TYPES = "Tag", "BeautifulSoup"


class HtmlWrapper(object):
    """
    An lxml adapter over a subset of the BeautifulSoup API
    """

    def __init__(self, html):
        if isinstance(html, (str, bytes)):
            self.html = fromstring(html)

        elif isinstance(html, HtmlWrapper):
            self.html = html.html

        elif isinstance(html, HtmlElement):
            self.html = html

        elif isinstance(html, BS4_TYPES):
            self.html = fromstring(str(html))

        else:
            msg = "Object of type %s not compatible with HtmlWrapper" % str(type(html))

            raise TypeError(msg)

    def __repr__(self):
        return 'HtmlWrapper: ' + repr(self.html)

    def __str__(self):
        return self.html.text

    def __getitem__(self, item):
        items = self.html.attrib[item]
        #
        # if ' ' in items:
        #     print(item, "items: ", items)

        if item == 'class':
            items = items.split(' ')

        return items

    def __getattr__(self, item):
        val = self.find(item)

        if val is None:
            if hasattr(self.html, item):
                return getattr(self.html, item)

            else:
                return None

        else:
            return val

    def name(self):
        return self.html.tag

    @property
    def text(self) -> str:
        text = self.html.text_content()

        return text if text else ''

    def find(self, tag: str, _class: str = None, **kwargs):
        return find(self.html, tag, _class, **kwargs)

    def find_all(self, tag: str, _class: str = None, *, gen=False, **kwargs) -> iter or tuple:
        return find_all(self.html, tag, _class, gen=gen, **kwargs)


def find(html: HtmlElement, tag: str,
         _class: str = None, **kwargs) -> HtmlWrapper or None:
    results = find_all(html, tag, _class, gen=True, **kwargs)

    return next(results) if results else None


def find_all(html: HtmlElement, tag: str,
             _class: str = None, gen: bool = False, **kwargs) -> iter or tuple:
    xpath = get_xpath(tag, _class, **kwargs)
    elems = xpath(html)

    if not elems:
        return tuple()

    wrapper_map = map(HtmlWrapper, elems)  # returns an iterator

    return wrapper_map if gen else tuple(wrapper_map)


def get_xpath_str(tag: str, _class: str = None, **kwargs) -> str:
    tag_xp = './/' + tag

    if _class:
        kwargs['class'] = _class

    for attr, val in kwargs.items():
        tag_xp += '['
        attr_xp = '@' + attr

        if isinstance(val, bool):
            if val:
                tag_xp += attr_xp

            else:
                tag_xp += 'not(%s)' % attr_xp

        elif isinstance(val, (set, list, tuple)):
            for item in val:
                val_xp = '"%s", ' % item

            val_xp = val_xp[:-2] if val else ''
            tag_xp += 'contains(%s, %s)' % (attr_xp, val_xp)

        elif isinstance(val, str):
            tag_xp += 'contains(%s, "%s")' % (attr_xp, val)

        else:
            tag_xp += "%s=%s'" % (attr_xp, val)

        tag_xp += ']'

    return tag_xp


@lru_cache(maxsize=None)
def get_xpath(tag: str, _class: str = None, **kwargs) -> XPath:
    xpath_str = get_xpath_str(tag, _class, **kwargs)

    return XPath(xpath_str)