import dbm
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import msgpack

from wiked.app.exc import NodeNotFound, PathNotFound


@dataclass
class Node:
    page_id: int
    title: str
    edges: Dict[int, str]

    def __hash__(self) -> int:
        return self.page_id

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.page_id == other.page_id
        elif isinstance(other, int):
            return self.page_id == other
        return NotImplemented

    def __contains__(self, item) -> bool:
        """
        Return True if the node links to the provided article ID.
        """
        if isinstance(item, Node) or isinstance(item, int):
            return item in self.edges
        return False

    def __getitem__(self, item) -> str:
        """
        Return visible value of an edge (text which is visible as link
        in article text).
        """
        return self.edges[item]


class Graph:
    def __init__(self, path: Path):
        self.db = dbm.open(path.as_posix(), "r")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __getitem__(self, key: int) -> Optional[Node]:
        key: bytes = msgpack.packb(key)
        try:
            value = self.db[key]
        except KeyError:
            return None
        return Node.loads(value)


class BFS:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.queue = []
        self.visited = set()

    def find_shortest_path(self, start: int, end: int) -> Tuple[int, ...]:
        if self.graph[start] is None:
            raise NodeNotFound(f"Start node {start} does not exist.")
        if self.graph[end] is None:
            raise NodeNotFound(f"End node {end} does not exist.")
        item = self.graph[start]
        if end in item.edges:
            return start, end
        for i in item.edges.keys() - self.visited:
            self.queue.append((start, i))
        while self.queue:
            current = self.queue.pop(0)
            item = self.graph[current[-1]]
            if end in item.edges:
                return (*current, end)
            for i in item.edges.keys() - self.visited:
                self.queue.append((*current, i))
        raise PathNotFound(f"Could not found any path from node {start} to node {end}.")
