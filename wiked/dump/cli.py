import dbm
from pathlib import Path
from time import time

import click
import msgpack

from wiked.dump.xml_parser import parse_wiki_dump


class DB:
    def __init__(self, path: Path, mode: str):
        self.db = dbm.open(path.as_posix(), mode)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __getitem__(self, key):
        key: bytes = msgpack.packb(key, use_bin_type=True)
        return msgpack.unpackb(self.db[key], use_list=True, raw=False)

    def __setitem__(self, key, value):
        key: bytes = msgpack.packb(key, use_bin_type=True)
        value: bytes = msgpack.packb(value, use_bin_type=True)
        self.db[key] = value


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
def main(filepath):
    filepath = Path(filepath)
    print(f"Processing {filepath.name}.")
    stem = filepath.name.split(".")[0]  # the file extension is .xml.bz2
    by_title_path = Path.cwd() / f"{stem}_by_title.db"
    by_id_path = Path.cwd() / f"{stem}_by_id.db"

    if by_title_path.is_file():
        print("Found existing title -> ID database.")
    else:
        print("Preparing title -> ID database...")
        start_timestamp = time()
        with DB(by_title_path, "n") as by_title_db:
            for item in parse_wiki_dump(filepath, skip_links=True):
                by_title_db[item[1]] = int(item[0])
        minutes, seconds = divmod(round(time() - start_timestamp), 60)
        print(f"Elapsed time: {minutes:02d}:{seconds:02d} (m:s). ")

    with DB(by_title_path, "r") as title_to_id:
        with DB(by_id_path, "n") as by_id_db:
            print("Preparing ID -> Node database...")
            start_timestamp = time()
            counter = 0
            for item in parse_wiki_dump(filepath):
                links = dict()
                for key, value in item[2].items():
                    try:
                        page_id = title_to_id[key]
                    except KeyError:
                        continue
                    links[page_id] = value
                by_id_db[item[0]] = (item[0], item[1], links)
                counter += 1
    minutes, seconds = divmod(round(time() - start_timestamp), 60)
    print(
        f"Finished! Elapsed time: {minutes:02d}:{seconds:02d} (m:s). "
        f"Articles: {counter}."
    )
