from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from wiked.app.exc import NodeNotFound, PathNotFound
from wiked.dump.db import DB


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

    def __iter__(self):
        """
        Iterate over page IDs this Node links to.
        """
        return iter(self.edges)


class Graph(DB):
    def __init__(self, path: Path):
        super().__init__(path, "r")

    def __getitem__(self, key: int) -> Node:
        title, edges = super().__getitem__(key)
        return Node(key, title, edges)

    def __setitem__(self, key, value):
        raise TypeError(f"'{Graph.__name__}' object does not support item assignment")

    def find_shortest_path(self, start_id: int, end_id: int) -> Tuple[Node, ...]:
        try:
            start_node = self[start_id]
        except KeyError:
            raise NodeNotFound(f"Start node {start_id} does not exist.")
        try:
            end_node = self[end_id]
        except KeyError:
            raise NodeNotFound(f"End node {end_id} does not exist.")

        if end_node in start_node:
            return start_node, end_node

        queue = [(start_id, x) for x in start_node]
        visited_or_queued = {start_id, *(x for x in start_node)}
        while queue:
            current_path = queue.pop(0)
            current_node = self[current_path[-1]]
            if end_node in current_node:
                return (*(self[x] for x in current_path), end_node)
            for x in current_node:
                if x not in visited_or_queued:
                    visited_or_queued.add(x)
                    queue.append((*current_path, x))
        raise PathNotFound(
            f"Could not found any path from node {start_id} to node {end_id}."
        )
