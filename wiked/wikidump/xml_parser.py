import logging
from pathlib import Path
from typing import (
    Generator,
    List,
    Tuple,
)
from xml.etree import ElementTree

from wiked.wikidump.link_parser import get_links_from_article

logger = logging.getLogger(__name__)


def parse_wiki_xml_dump(xml_path: Path) -> Generator[Tuple[str, int, List[str]]]:
    page_counter = 0
    skip_page = False
    for event, element in ElementTree.iterparse(
        xml_path.as_posix(), events=("start", "end")
    ):
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
                skip_page = True
            elif tag_name == "text":
                text = element.text
            elif tag_name == "page":
                page_counter += 1
                yield (title, page_id, get_links_from_article(text))

    logger.info(f"Found {page_counter} articles.")


