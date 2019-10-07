import bz2
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple

from lxml import etree

from wiked.dump.link_parser import get_visible_links_from_article


def remove_xml_element(element):
    # https://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files#7171543
    element.clear()
    for ancestor in element.xpath("ancestor-or-self::*"):
        while ancestor.getprevious() is not None:
            del ancestor.getparent()[0]


def parse_wiki_dump(
    xml_bz2_path: Path, skip_links: bool = False
) -> Generator[Tuple[int, str, Optional[Dict[str, str]]], None, None]:
    skip_page = False
    with bz2.open(xml_bz2_path.as_posix(), "rb") as file:
        for event, element in etree.iterparse(file, events=("start", "end")):
            tag_name = element.tag.split("}")[1]

            if event == "start" and tag_name == "page":
                skip_page = False
                title = None
                page_id = None
                text = None
            elif event == "end" and not skip_page:
                if tag_name == "title":
                    title = element.text
                elif tag_name == "ns":
                    if int(element.text) != 0:
                        skip_page = True
                elif tag_name == "id" and page_id is None:
                    page_id = int(element.text)
                elif tag_name == "redirect":
                    if skip_links:
                        yield (page_id, title, None)
                    else:
                        yield (page_id, title, {element.attrib["title"]: "redirect"})
                    skip_page = True
                    remove_xml_element(element)
                elif tag_name == "text":
                    text = element.text
                elif tag_name == "page":
                    if skip_links:
                        yield (page_id, title, None)
                    else:
                        yield (page_id, title, get_visible_links_from_article(text))
                    remove_xml_element(element)
