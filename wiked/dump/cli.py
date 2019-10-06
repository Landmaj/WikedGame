import dbm
from pathlib import Path
from time import time

import click

from wiked.app.graph import Graph, Node
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
        with Graph(output_file, "n") as graph:
            print("Preparing final database...")
            start_timestamp = time()
            counter = 0
            for item in parse_wiki_dump(filepath):
                links = set()
                for title in item[2]:
                    try:
                        page_id = title_to_id[title]
                    except KeyError:
                        continue
                    links.add(int(page_id))
                graph[item[0]] = Node(item[0], item[1], links)
                counter += 1
    minutes, seconds = divmod(round(time() - start_timestamp), 60)
    print(
        f"Finished! Elapsed time: {minutes:02d}:{seconds:02d} (m:s). "
        f"Articles: {counter}."
    )
