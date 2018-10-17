import csv
import logging
import mmap
import os
import re
from time import time
from datetime import datetime
import psutil

logger = logging.getLogger(__name__)


def get_memory_usage() -> str:
    memory_info = psutil.Process(os.getpid()).memory_full_info()
    unique_memory = round(int(memory_info.uss) / 1024 ** 2)
    total_memory = round(int(memory_info.vms) / 1024 ** 2)
    return (
        f"[{datetime.now().strftime('%H:%M:%S')}] Memory usage: "
        f"[total] {total_memory} MB | [unique] {unique_memory} MB."
    )


# https://www.mediawiki.org/wiki/Manual:Page_table
# GROUP     DATA TYPE                                    EXAMPLE
# (0)       int(8) unsigned NOT NULL AUTO_INCREMENT      2
# (1)       int(11) NOT NULL DEFAULT '0'                 0
# (2)       varbinary(255) NOT NULL DEFAULT ''           'AWK'
# (3)       tinyblob NOT NULL                            ''
# (4)       bigint(20) unsigned NOT NULL DEFAULT '0'     329
# (5)       tinyint(1) unsigned NOT NULL DEFAULT '0'     0
# (6)       tinyint(1) unsigned NOT NULL DEFAULT '0'     0
# (7)       double unsigned NOT NULL DEFAULT '0'         0.487812640599732
# (8)       varbinary(14) NOT NULL DEFAULT ''            '20180926204147'
# (9)      varbinary(14) DEFAULT NULL                   '20180926204705'
# (10)      int(8) unsigned NOT NULL DEFAULT '0'         54200939
# (11)      int(8) unsigned NOT NULL DEFAULT '0'         17903
# (12)      tinyint(1) NOT NULL DEFAULT '0'              0
# (14)      varbinary(32) DEFAULT NULL                   'wikitext'
# (16)      varbinary(35) DEFAULT NULL                   NULL

page_pattern = re.compile(
    b"\("
    b"(\d+),"                # (0)  page_id
    b"(\d+),"                # (1)  page_namespace
    b"'(.*?)',"              # (2)  page_title
    b"'(.*?)',"              # (3)  page_restrictions
    b"(\d+),"                # (4)  page_counter
    b"([01]),"               # (5)  page_is_redirect
    b"([01]),"               # (6)  page_is_new
    b"(\d+\.\d+),"           # (7)  page_random
    b"'(\d+)',"              # (8)  page_touched
    b"('(\d+)'|NULL),"       # (9) page_links_updated
    b"(\d+),"                # (10) page_latest
    b"(\d+),"                # (11) page_len
    b"([01]),"               # (12) page_no_title_convert
    b"('(.*?)',|NULL)"       # (14) page_content_model
    b"('(.*?)',|NULL)"       # (16) page_lang
    b"\)",
    re.DOTALL,
)

# https://www.mediawiki.org/wiki/Manual:Pagelinks_table#
# GROUP    DATA TYPE                                    EXAMPLE
# (1)      int(8) unsigned NOT NULL DEFAULT '0'         654181
# (2)      int(11) NOT NULL DEFAULT '0'                 0
# (3)      varbinary(255) NOT NULL DEFAULT ''           "Fallen_Angels"
# (4)      int(11) NOT NULL DEFAULT '0'                 0

link_pattern = re.compile(
    b"\("
    b"(\d+),"                # (1)  pl_id
    b"(\d+),"                # (2)  pl_namespace
    b"'(.*?)',"              # (3)  pl_title
    b"(\d+)"                 # (4)  pl_from_namespace
    b"\)",
    re.DOTALL,
)


class PageRegexGroup:
    WIKI_ID = 0
    NAMESPACE = 1
    TITLE = 2
    REDIRECT = 5
    MODIFIED = 8


class LinkRegexGroup:
    FROM_WIKI_ID = 0
    FROM_NAMESPACE = 3
    TO_TITLE = 2
    TO_NAMESPACE = 1


MAIN_NAMESPACE = b"0"


def parse_page_sql(page_path: str, link_path: str):
    start_timestamp = time()

    article_to_id = dict()
    article_ids = set()
    with open(page_path, "rb") as page_dump:
        start = time()
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] Starting page matching..."
        )
        with mmap.mmap(page_dump.fileno(), 0, access=mmap.ACCESS_READ) as node_match:
            with open("/home/landmaj/PycharmProjects/WikedGame/page.csv", "w") as file:
                writer = csv.writer(file)
                for match in re.finditer(page_pattern, node_match):
                    match = match.groups()
                    if (
                        match[PageRegexGroup.NAMESPACE] == MAIN_NAMESPACE
                        and match[PageRegexGroup.TITLE] != b""
                    ):
                        wiki_id = int(match[PageRegexGroup.WIKI_ID])
                        redirect = bool(int(match[PageRegexGroup.REDIRECT]))
                        title = match[PageRegexGroup.TITLE].decode("utf-8")
                        writer.writerow(("Page", wiki_id, redirect, title))
                        article_to_id[title] = wiki_id
                        article_ids.add(wiki_id)
                os.chmod(file.name, 0o664)
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] File page.csv created "
                    f"after {round(time() - start)} seconds."
                )
                print(get_memory_usage())

    with open(link_path, "rb") as link_dump:
        start = time()
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] Starting link matching..."
        )
        with mmap.mmap(link_dump.fileno(), 0, access=mmap.ACCESS_READ) as rel_match:
            with open("/home/landmaj/PycharmProjects/WikedGame/link.csv", "w") as file:
                writer = csv.writer(file)
                for match in re.finditer(link_pattern, rel_match):
                    match = match.groups()
                    from_wiki_id = int(match[LinkRegexGroup.FROM_WIKI_ID])
                    if (
                        match[LinkRegexGroup.FROM_NAMESPACE] == MAIN_NAMESPACE
                        and match[LinkRegexGroup.TO_NAMESPACE] == MAIN_NAMESPACE
                        and match[LinkRegexGroup.TO_TITLE] != b""
                        and from_wiki_id in article_ids
                    ):
                        try:
                            to_wiki_id = article_to_id[match[LinkRegexGroup.TO_TITLE].decode("utf-8")]
                        except KeyError:
                            continue
                        else:
                            writer.writerow((from_wiki_id, to_wiki_id, "LINKS_TO"))
                os.chmod(file.name, 0o664)
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] File link.csv created "
                    f"after {round(time() - start)} seconds."
                )
                print(get_memory_usage())

    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] "
        f"Time elapsed: {round(time() - start_timestamp)} seconds. "
    )
