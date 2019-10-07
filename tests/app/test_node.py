import pytest

from wiked.app.graph import Node


def test_node_creation():
    node1 = Node(1, "Title", {2: "Title2", 3: "Title3"})
    node2 = Node(2, "Title2", {})
    assert node1.page_id == 1
    assert node1.title == "Title"
    assert node1.edges == {2: "Title2", 3: "Title3"}
    assert node2.page_id == 2
    assert node2.title == "Title2"
    assert node2.edges == {}


@pytest.mark.parametrize(
    ["page_id", "title", "links"],
    [
        (1, "Title", {2: "Title2", 3: "Title3"}),
        (2, "2137", {2: "Title2", 3: None}),
        (1, "Title", {}),
    ],
)
def test_serialization_and_deserialization(page_id, title, links):
    node = Node(page_id, title, links)
    serialized_node = node.dumps()
    assert isinstance(serialized_node, bytes)
    deserialized_node = Node.loads(serialized_node)
    assert isinstance(deserialized_node, Node)
    assert deserialized_node.page_id == page_id
    assert deserialized_node.title == title
    assert node.edges == links


@pytest.mark.parametrize(
    ["container", "expected_result"],
    [
        ([1, 2, 3], True),
        ({1, 2, 3}, True),
        ((1, 2, 3), True),
        ({1: 1, 2: 2, 3: 3}, True),
        ([2, 3, 4], False),
        ({2, 3, 4}, False),
        ((2, 3, 4), False),
        ({2: 2, 3: 3, 4: 4}, False),
        ([Node(1, "Title", {}), Node(2, "", {})], True),
        ([Node(2, "Title", {}), Node(3, "", {})], False),
        (("1", "2", "3"), False),
        ((1.0, 2.0, 3.0), False),
    ],
)
def test_node_in(container, expected_result):
    node = Node(1, "Title", {})
    result = node in container
    assert result is expected_result


@pytest.mark.parametrize(
    ["links", "value", "expected_result"],
    [
        ({2137: "2137", 7312: "7312"}, 2137, True),
        ({7312: "7312", 1: "1"}, 2137, False),
        ({7312: "7312", 1: "2137"}, 2137, False),
        ({"2137": "2137", "7312": "7312"}, 2137, False),
        ({2137.0: "2137", 7312.0: "7312"}, 2137, True),
        ({2137: "2137", 7312: "7312"}, Node(2137, "Title", {}), True),
        ({2137: "2137", 7312: "7312"}, "2137", False),
    ],
)
def test_contains(links, value, expected_result):
    node = Node(1, "Title", links)
    result = value in node
    assert result is expected_result


def test_getitem():
    node1 = Node(1, "Title", {2: "Title2", 3: "Title3"})
    node2 = Node(2, "Title2", {})
    assert node1[2] == "Title2"
    assert node1[3] == "Title3"
    assert node1[node2] == "Title2"
    for key in (1, "2"):
        with pytest.raises(KeyError):
            assert node1[key]


def test_setitem():
    node1 = Node(1, "Title", {2: "Title2", 3: "Title3"})
    node2 = Node(2, "Title2", {})
    node1[2] = "2137"
    assert node1.edges == {2: "2137", 3: "Title3"}
    node1[node2] = "7312"
    assert node1.edges == {2: "7312", 3: "Title3"}
    with pytest.raises(TypeError):
        node1["2"] = "2137"
