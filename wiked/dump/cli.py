import dbm
import os
import pickle
from pathlib import Path
from time import time

import click

from wiked.app.node import Node
from wiked.dump.xml_parser import parse_wiki_dump


@click.command()
@click.argument("language")
@click.argument("filepath", type=click.Path(exists=True))
def main(language, filepath):
    filepath = Path(filepath)
    try:
        with dbm.open("tmp.dmb", "n") as title_to_id:
            print("Preparing temporary title to ID database...")
            for item in parse_wiki_dump(filepath, skip_links=True):
                title_to_id[item[1]] = str(item[0])
            with dbm.open(f"{language}_{int(time())}.dbm", "n") as db:
                print("\nPreparing database...")
                for item in parse_wiki_dump(filepath):
                    links = set()
                    for title in item[2].keys():
                        try:
                            page_id = db[title]
                        except KeyError:
                            continue
                        links.add(int(page_id))
                    db[pickle.dumps(item[0])] = (Node(item[0], item[1], links)).dumps()
    finally:
        os.remove("tmp.dbm")
        print("\nFinished!")
