import bz2
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple

from lxml import etree

from wiked.dump.link_parser import get_links_from_article


def remove_xml_element(element):
    # https://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files#7171543
    element.clear()
    for ancestor in element.xpath("ancestor-or-self::*"):
        while ancestor.getprevious() is not None:
            del ancestor.getparent()[0]


NAMESPACES = {"wiki": "http://www.mediawiki.org/xml/export-0.10/"}
NS = etree.XPath(
    ".//wiki:ns/text()", namespaces=NAMESPACES, smart_strings=False, regexp=False
)
PAGE_ID = etree.XPath(
    ".//wiki:id/text()", namespaces=NAMESPACES, smart_strings=False, regexp=False
)
TITLE = etree.XPath(
    ".//wiki:title/text()", namespaces=NAMESPACES, smart_strings=False, regexp=False
)
REDIRECT = etree.XPath(
    ".//wiki:redirect/@title", namespaces=NAMESPACES, smart_strings=False, regexp=False
)
TEXT = etree.XPath(
    ".//wiki:revision/wiki:text/text()",
    namespaces=NAMESPACES,
    smart_strings=False,
    regexp=False,
)


def parse_wiki_dump(
    xml_bz2_path: Path, skip_links: bool = False
) -> Generator[Tuple[int, str, Optional[Dict[str, str]]], None, None]:
    with bz2.open(xml_bz2_path.as_posix(), "rb") as file:
        for event, element in etree.iterparse(
            file, events=("end",), tag="{http://www.mediawiki.org/xml/export-0.10/}page"
        ):
            if int(NS(element)[0]) != 0:  # 0 is the main namespace
                continue
            page_id = int(PAGE_ID(element)[0])
            title = TITLE(element)[0]
            if skip_links:
                yield (page_id, title)
            elif bool(REDIRECT(element)):
                yield (page_id, title, {REDIRECT(element)[0]: None})
            else:
                yield (page_id, title, get_links_from_article(TEXT(element)[0]))
            remove_xml_element(element)
