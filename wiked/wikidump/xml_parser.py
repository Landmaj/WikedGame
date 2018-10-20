import logging
import time
from pathlib import Path
from typing import Dict, Generator, Tuple

from lxml import etree

from wiked.wikidump.link_parser import get_links_from_article

logger = logging.getLogger(__name__)


def parse_wiki_dump(
    xml_path: Path
) -> Generator[Tuple[str, int, Dict[str, str]], None, None]:
    start_timestamp = time.time()
    logger.info(f"Parsing {xml_path.name}")
    page_counter = 0
    skip_page = False
    for event, element in etree.iterparse(xml_path.as_posix(), events=("start", "end")):
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
                if page_counter % 100_000 == 0:
                    print(f"Processed {page_counter} articles.")

                # https://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files#7171543
                element.clear()
                for ancestor in element.xpath("ancestor-or-self::*"):
                    while ancestor.getprevious() is not None:
                        del ancestor.getparent()[0]

                yield (title, page_id, get_links_from_article(text))

    logger.info(f"Found {page_counter} articles.")
    logger.info(f"Elapsed time {round(time.time() - start_timestamp)} seconds.")
