import logging
import time
from pathlib import Path
from typing import Dict, Generator, Tuple
from xml.etree import ElementTree

from wiked.wikidump.link_parser import get_links_from_article

logger = logging.getLogger(__name__)


def parse_wiki_dump(
    xml_path: Path
) -> Generator[Tuple[str, int, Dict[str, str]], None, None]:
    start_timestamp = time.time()
    logger.info(f"Parsing {xml_path.name}")
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
                if page_counter % 100_000 == 0:
                    print(f"Processed {page_counter} articles.")
                yield (title, page_id, get_links_from_article(text))

    logger.info(f"Found {page_counter} articles.")
    logger.info(f"Elapsed time {round(time.time() - start_timestamp)} seconds.")
