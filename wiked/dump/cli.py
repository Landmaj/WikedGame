import dbm
import os
from pathlib import Path
from time import time

import click

from wiked.app.graph import Graph, Node
from wiked.dump.xml_parser import parse_wiki_dump


@click.command()
@click.argument("language")
@click.argument("filepath", type=click.Path(exists=True))
def main(language, filepath):
    filepath = Path(filepath)
    tmp_file = "tmp.db"
    start_timestamp = time()
    print(f"Parsing {filepath.name}")
    try:
        with dbm.open(tmp_file, "n") as title_to_id:
            print("Preparing temporary title to ID database...")
            for item in parse_wiki_dump(filepath, skip_links=True):
                title_to_id[item[1]] = str(item[0])
            with Graph(Path.cwd() / f"{language}_{int(time())}.db", "n") as graph:
                print("Preparing database...")
                for item in parse_wiki_dump(filepath):
                    links = set()
                    for title in item[2]:
                        try:
                            page_id = title_to_id[title]
                        except KeyError:
                            continue
                        links.add(int(page_id))
                    graph[item[0]] = Node(item[0], item[1], links)
    finally:
        os.remove(tmp_file)
        minutes, seconds = divmod(round(time() - start_timestamp), 60)
        print(f"Finished! Elapsed time: {minutes:02d}:{seconds:02d} (m:s).")
