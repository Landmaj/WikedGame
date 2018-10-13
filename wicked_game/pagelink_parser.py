import logging
import mmap
import re
import sys
from time import time

MAIN_NAMESPACE = b"0"

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
logger.addHandler(logging.StreamHandler())


# https://www.mediawiki.org/wiki/Manual:Pagelinks_table#
# GROUP    DATA TYPE                                    EXAMPLE
# (1)      int(8) unsigned NOT NULL DEFAULT '0'         654181
# (2)      int(11) NOT NULL DEFAULT '0'                 0
# (3)      varbinary(255) NOT NULL DEFAULT ''           "Fallen_Angels"
# (4)      int(11) NOT NULL DEFAULT '0'                 0

pattern = re.compile(
    b"\("
    b"(\d+),"                # (1)  pl_id
    b"(\d+),"                # (2)  pl_namespace
    b"'(.*?)',"              # (3)  pl_title
    b"(\d+)"                 # (4)  pl_from_namespace
    b"\)"
)

counter = 0
total_size = 0
pagelinks = set()
file_path = "/home/landmaj/Downloads/plwiki-20181001-pagelinks.sql"
with open(file_path, "rb") as file:
    start_timestamp = time()
    with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as m:
        for match in pattern.finditer(m):
            if match[2] == MAIN_NAMESPACE:
                counter += 1
                total_size += sys.getsizeof(
                    (int(match[1]), match[2].decode("utf-8").replace("_", " "))
                )
            # print(
            #     int(match[1]),
            #     match[3].decode("utf-8")
            # )
    end_timestamp = time()

logger.info(
    "Execution time: {} seconds."
    .format(round(end_timestamp - start_timestamp))
)
logger.info(
    "Items: {}".format(counter)
)
logger.info(
    "Total size: {} MB".format(round(total_size/1024/1024))
)
