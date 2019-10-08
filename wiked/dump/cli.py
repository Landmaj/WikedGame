import dbm.gnu
from multiprocessing import Process, Queue
from pathlib import Path
from time import time

import click
import msgpack

from wiked.dump.link_parser import get_links_from_article
from wiked.dump.xml_parser import parse_wiki_generator, parse_wiki_process


class DB:
    def __init__(self, path: Path, mode: str):
        self.db = dbm.gnu.open(path.as_posix(), mode)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __getitem__(self, key):
        if not isinstance(key, bytes):
            key: bytes = msgpack.packb(key, use_bin_type=True)
        return msgpack.unpackb(self.db[key], use_list=True, raw=False)

    def __setitem__(self, key, value):
        key: bytes = msgpack.packb(key, use_bin_type=True)
        value: bytes = msgpack.packb(value, use_bin_type=True)
        self.db[key] = value

    def keys(self):
        return self.db.keys()


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
def main(filepath):
    input_file = Path(filepath)
    print(f"Processing {input_file.name}.")
    stem = input_file.name.split(".")[0]  # the file extension is .xml.bz2

    print("Preparing title -> ID database...")
    start_timestamp = time()
    by_title_path = Path.cwd() / f"{stem}_by_title.db"
    with DB(by_title_path, "nf") as by_title:
        for value in parse_wiki_generator(input_file):
            by_title[value[1]] = int(value[0])
    minutes, seconds = divmod(round(time() - start_timestamp), 60)
    print(f"Elapsed time: {minutes:02d}:{seconds:02d} (m:s).")

    print("Preparing ID -> Node database...")
    start_timestamp = time()
    by_id_path = Path.cwd() / f"{stem}_by_id.db"
    rx = Queue()
    xml_parser = Process(target=parse_wiki_process, daemon=True, args=(input_file, rx))
    with DB(by_title_path, "r") as title_to_id:
        with DB(by_id_path, "nf") as by_id:
            xml_parser.start()
            articles = 0
            redirects = 0
            while True:
                value = rx.get()
                if value is None:  # queue is empty
                    break
                elif value[2]:  # redirect
                    interim_links = {value[2]: None}
                    redirects += 1
                else:  # article
                    interim_links = get_links_from_article(value[3])
                    articles += 1
                links = {}
                for title, visible in interim_links.items():
                    try:
                        links[title_to_id[title]] = visible
                    except KeyError:
                        pass
                by_id[value[0]] = (value[1], links)
    minutes, seconds = divmod(round(time() - start_timestamp), 60)
    print(f"Elapsed time: {minutes:02d}:{seconds:02d} (m:s).")
    print(
        f"Articles: {articles}, redirects: {redirects}, total: {articles + redirects}."
    )
