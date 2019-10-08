import bz2
from multiprocessing import Queue
from pathlib import Path
from typing import Generator, Tuple

from lxml import etree


def remove_xml_element(element):
    # https://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files#7171543
    element.clear()
    for ancestor in element.xpath("ancestor-or-self::*"):
        while ancestor.getprevious() is not None:
            del ancestor.getparent()[0]


kwargs = {
    "namespaces": {"wiki": "http://www.mediawiki.org/xml/export-0.10/"},
    "smart_strings": False,
    "regexp": False,
}
xpath_ns = etree.XPath(".//wiki:ns/text()", **kwargs)
xpath_page_id = etree.XPath(".//wiki:id/text()", **kwargs)
xpath_title = etree.XPath(".//wiki:title/text()", **kwargs)
xpath_redirect = etree.XPath(".//wiki:redirect/@title", **kwargs)
xpath_text = etree.XPath(".//wiki:revision/wiki:text/text()", **kwargs)


def parse_wiki_generator(xml_file: Path) -> Generator[Tuple[int, str], None, None]:
    with bz2.open(xml_file.as_posix(), "rb") as file:
        for event, element in etree.iterparse(
            file, events=("end",), tag="{http://www.mediawiki.org/xml/export-0.10/}page"
        ):
            if int(xpath_ns(element)[0]) != 0:  # 0 is the main namespace
                continue
            page_id = int(xpath_page_id(element)[0])
            title = xpath_title(element)[0]
            yield (page_id, title)
            remove_xml_element(element)


def parse_wiki_process(xml_file: Path, tx: Queue) -> None:
    with bz2.open(xml_file.as_posix(), "rb") as file:
        """
        If redirect -> (page_id: int, title: str, redirect_to: str, None)
        Else -> (page_id: int, title: str, None, article_body: str)
        """
        for event, element in etree.iterparse(
            file, events=("end",), tag="{http://www.mediawiki.org/xml/export-0.10/}page"
        ):
            if int(xpath_ns(element)[0]) != 0:  # 0 is the main namespace
                continue
            page_id = int(xpath_page_id(element)[0])
            title = xpath_title(element)[0]
            if bool(xpath_redirect(element)):
                tx.put((page_id, title, xpath_redirect(element)[0], None))
            else:
                tx.put((page_id, title, None, xpath_text(element)[0]))
            remove_xml_element(element)
        tx.put(None)  # inform receiver that no more data will be sent
