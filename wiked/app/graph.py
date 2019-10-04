import dbm
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set, Tuple

import msgpack

from wiked.app.exc import GraphError, NodeNotFound, PathNotFound


@dataclass
class Node:
    page_id: int
    title: str
    links: Set[int]

    def __hash__(self) -> int:
        return self.page_id

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.page_id == other.page_id
        elif isinstance(other, int):
            return self.page_id == other
        return NotImplemented

    def dumps(self) -> bytes:
        data = (self.page_id, self.title, list(self.links))
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def loads(serialized_node: bytes) -> "Node":
        data = msgpack.unpackb(serialized_node, use_list=False, raw=False)
        return Node(data[0], data[1], {*data[2]})


class Graph:
    def __init__(self, path: Path, mode: str = "r"):
        self.db = dbm.open(path.as_posix(), mode)
        self.mode = mode
        self.language = path.stem.split("_")[0]

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

    def __setitem__(self, key: int, value: Node) -> None:
        if self.mode == "r":
            raise GraphError("Setting values is not allowed in read mode.")
        if not isinstance(value, Node):
            raise GraphError(
                f"Value must be of type {Node.__name__}, not {type(value)}."
            )
        key: bytes = msgpack.packb(key)
        self.db[key] = value.dumps()


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
        if end in item.links:
            return start, end
        for i in item.links - self.visited:
            self.queue.append((start, i))
        while self.queue:
            current = self.queue.pop(0)
            item = self.graph[current[-1]]
            if end in item.links:
                return (*current, end)
            for i in item.links - self.visited:
                self.queue.append((*current, i))
        raise PathNotFound(f"Could not found any path from node {start} to node {end}.")
