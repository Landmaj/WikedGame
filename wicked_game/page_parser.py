import logging
import mmap
import re
import sys
from time import time

MAIN_NAMESPACE = b"0"

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
logger.addHandler(logging.StreamHandler())

# https://www.mediawiki.org/wiki/Manual:Page_table
# GROUP     DATA TYPE                                    EXAMPLE
# (1)       int(8) unsigned NOT NULL AUTO_INCREMENT      2
# (2)       int(11) NOT NULL DEFAULT '0'                 0
# (3)       varbinary(255) NOT NULL DEFAULT ''           'AWK'
# (4)       tinyblob NOT NULL                            ''
# (5)       bigint(20) unsigned NOT NULL DEFAULT '0'     329
# (6)       tinyint(1) unsigned NOT NULL DEFAULT '0'     0
# (7)       tinyint(1) unsigned NOT NULL DEFAULT '0'     0
# (8)       double unsigned NOT NULL DEFAULT '0'         0.487812640599732
# (9)       varbinary(14) NOT NULL DEFAULT ''            '20180926204147'
# (11)      varbinary(14) DEFAULT NULL                   '20180926204705'
# (12)      int(8) unsigned NOT NULL DEFAULT '0'         54200939
# (13)      int(8) unsigned NOT NULL DEFAULT '0'         17903
# (14)      tinyint(1) NOT NULL DEFAULT '0'              0
# (16)      varbinary(32) DEFAULT NULL                   'wikitext'
# (18)      varbinary(35) DEFAULT NULL                   NULL

pattern = re.compile(
    b"\("
    b"(\d+),"                # (1)  page_id
    b"(\d+),"                # (2)  page_namespace
    b"'(.*?)',"              # (3)  page_title
    b"'(.*?)',"              # (4)  page_restrictions
    b"(\d+),"                # (5)  page_counter
    b"([01]),"               # (6)  page_is_redirect
    b"([01]),"               # (7)  page_is_new
    b"(\d+\.\d+),"           # (8)  page_random
    b"'(\d+)',"              # (9)  page_touched
    b"('(\d+)'|NULL),"       # (11) page_links_updated
    b"(\d+),"                # (12) page_latest
    b"(\d+),"                # (13) page_len
    b"([01]),"               # (14) page_no_title_convert
    b"('(.*?)',|NULL)"       # (16) page_content_model
    b"('(.*?)',|NULL)"       # (18) page_lang
    b"\)"
)

articles = set()
file_path = "/home/landmaj/Downloads/plwiki-20181001-page.sql"
with open(file_path, "rb") as file:
    start_timestamp = time()
    with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as m:
        for match in pattern.finditer(m):
            if match[2] == MAIN_NAMESPACE:
                articles.add((
                    int(match[1]),  # page ID
                    match[3].decode("utf-8").replace("_", " "),  # page title
                    bool(int(match[6])),  # if page is a redirect
                    int(match[9]),  # last modified timestamp
                ))
    end_timestamp = time()

logger.info(
    "Execution time: {} seconds."
    .format(round(end_timestamp - start_timestamp))
)
logger.info(
    "Items: {}".format(len(articles))
)
logger.info(
    "Size of the set: {} MB".format(round(sys.getsizeof(articles)/1024/1024))
)
