class GraphError(Exception):
    pass


class TimeoutExceeded(GraphError):
    pass


class PathNotFound(GraphError):
    pass


class NodeNotFound(GraphError):
    pass
