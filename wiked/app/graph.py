from collections import deque
from typing import List, Tuple

from wiked.app.models import WikiPage


def is_directly_linked(page: WikiPage, destination: WikiPage) -> bool:
    return destination in page.links


def find_links(
    page: WikiPage, path: Tuple["WikiPage", ...]
) -> List[Tuple["WikiPage", ...]]:
    result = []
    for link in page.links:
        result.append(path + (link,))
    return result


def find_shortest_path(start: WikiPage, destination: WikiPage) -> Tuple[WikiPage, ...]:
    """
    TODO: this solution will probably take an enormous amount of memory
          but for MVP it should do
    """

    if is_directly_linked(start, destination):
        return start, destination
    else:
        queue = deque()
        queue.extend(find_links(start, (start,)))
        for path in queue:
            if is_directly_linked(path[-1], destination):
                return path + (destination,)
            else:
                queue.append(find_links(path[-1], path))
    return ()
