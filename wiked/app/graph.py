import dbm
import pickle
from pathlib import Path
from typing import Optional, Tuple

from wiked.app.exc import NodeNotFound, PathNotFound
from wiked.app.node import Node


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
