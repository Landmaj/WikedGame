import pickle
from typing import Set


class Node(tuple):
    def __new__(cls, page_id: int, title: str, links: Set[int]):
        return tuple.__new__(Node, (page_id, title, links))

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

    def dump(self):
        return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)
