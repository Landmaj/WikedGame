import dbm
from pathlib import Path
from time import time

import click
import msgpack

from wiked.dump.xml_parser import parse_wiki_dump


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
def main(filepath):
    filepath = Path(filepath)
    print(f"Processing {filepath.name}.")
    stem = filepath.name.split(".")[0]  # the file extension is .xml.bz2
    intermediate_database = Path.cwd() / f"{stem}_inter.db"
    output_file = Path.cwd() / f"{stem}_final.db"

    if intermediate_database.is_file():
        print("Found existing intermediate database.")
    else:
        print("Preparing intermediate database...")
        start_timestamp = time()
        with dbm.open(intermediate_database.as_posix(), "n") as inter_db:
            for item in parse_wiki_dump(filepath, skip_links=True):
                inter_db[item[1]] = str(item[0])
        minutes, seconds = divmod(round(time() - start_timestamp), 60)
        print(f"Elapsed time: {minutes:02d}:{seconds:02d} (m:s). ")

    with dbm.open(intermediate_database.as_posix(), "r") as title_to_id:
        with dbm.open(output_file.as_posix(), "n") as db:
            print("Preparing final database...")
            start_timestamp = time()
            counter = 0
            for item in parse_wiki_dump(filepath):
                links = dict()
                for key, value in item[2].items():
                    try:
                        page_id = int(title_to_id[key])
                    except KeyError:
                        continue
                    links[page_id] = value
                db[msgpack.packb(item[0])] = msgpack.packb(
                    (item[0], item[1], links), use_bin_type=True
                )
                counter += 1
    minutes, seconds = divmod(round(time() - start_timestamp), 60)
    print(
        f"Finished! Elapsed time: {minutes:02d}:{seconds:02d} (m:s). "
        f"Articles: {counter}."
    )
