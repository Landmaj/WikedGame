import csv
from pathlib import Path

from wiked.wikidump.xml_parser import parse_wiki_dump


def generate_neo4j_csv(xml_path: Path, output_dir: Path):
    node_csv = (output_dir / "node.csv").as_posix()
    rel_csv = (output_dir / "relation.csv").as_posix()

    with open(node_csv, "w", encoding="utf-8") as node_f, open(
        rel_csv, "w", encoding="UTF=8"
    ) as rel_f:
        node_writer = csv.writer(node_f, delimiter=",", lineterminator="\n")
        rel_writer = csv.writer(rel_f, delimiter=",", lineterminator="\n")

        node_writer.writerow([":LABEL", "title:ID", "page_id:int"])
        rel_writer.writerow([":START_ID", ":TYPE", ":END_ID", "link_description"])

        for page in parse_wiki_dump(xml_path):
            node_writer.writerow(["Page", page[0], page[1]])
            for rel in page[2]:
                rel_writer.writerow([page[0], "LINKS_TO", rel[0], rel[1]])
