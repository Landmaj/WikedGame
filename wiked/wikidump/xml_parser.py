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
    logger.info(f"Parsing {xml_path.name}")
    start_timestamp = time.time()
    file_size = xml_path.stat().st_size

    page_counter = 0
    skip_page = False
    with open(xml_path.as_posix(), "rb") as file:
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
                    skip_page = True
                elif tag_name == "text":
                    text = element.text
                elif tag_name == "page":
                    page_counter += 1
                    if page_counter % 1000 == 0:
                        bytes_per_second = file.tell() / (time.time() - start_timestamp)
                        minutes, seconds = divmod(
                            (file_size - file.tell()) / bytes_per_second, 60
                        )
                        print(f"Processed {page_counter} articles.", end=" ")
                        print(
                            f"ETA: {round(minutes):02d}:{round(seconds):02d} (m:s)",
                            end="\r",
                        )

                    # https://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files#7171543
                    element.clear()
                    for ancestor in element.xpath("ancestor-or-self::*"):
                        while ancestor.getprevious() is not None:
                            del ancestor.getparent()[0]

                    yield (title, page_id, get_links_from_article(text))

    logger.info(f"Found {page_counter} articles.")
    minutes, seconds = divmod(round(time.time() - start_timestamp), 60)
    logger.info(f"Elapsed time: {minutes:02d}:{seconds:02d} (m:s).")
