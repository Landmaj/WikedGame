import dbm
import pickle
from pathlib import Path
from typing import Optional, Set, Tuple

from wiked.app.exc import NodeNotFound, PathNotFound


class Node(tuple):
    def __new__(cls, page_id: int, title: str, links: Set[int]):
        return tuple.__new__(Node, (page_id, title, links))

    def __getnewargs__(self):
        return self.page_id, self.title, self.links

    def __hash__(self) -> int:
        return self.page_id

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.page_id == other.page_id
        elif isinstance(other, int):
            return self.page_id == other
        return NotImplemented

    @property
    def page_id(self) -> int:
        return self[0]

    @property
    def title(self) -> str:
        return self[1]

    @property
    def links(self) -> Set[int]:
        return self[2]

    def dumps(self):
        return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)


class Graph:
    def __init__(self, path: Path):
        self.db = dbm.open(path.as_posix(), "r")
        self.language = path.stem.split("_")[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __getitem__(self, item) -> Optional[Node]:
        key = pickle.dumps(item)
        try:
            value = self.db[key]
        except KeyError:
            return None
        return pickle.loads(value)


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
