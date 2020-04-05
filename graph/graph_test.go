package graph

import (
	"testing"
)

type inMemoryStorage map[uint32]Node

func (s *inMemoryStorage) GetNode(i uint32) (Node, error) {
	if n, ok := (*s)[i]; ok {
		return n, nil
	}
	return Node{}, ErrNodeNotFound
}

func TestShortestPath(t *testing.T) {
	n1 := NewNode(1, "one", 2, 3)
	n2 := NewNode(2, "two", 1, 4)
	n3 := NewNode(3, "three", 2)
	n4 := NewNode(4, "four", 5)
	n5 := NewNode(5, "five", 2)
	n6 := NewNode(6, "six", 7)
	n7 := NewNode(7, "seven")
	storage := inMemoryStorage{1: n1, 2: n2, 3: n3, 4: n4, 5: n5, 6: n6, 7: n7}
	graph := Graph{backend: &storage}

	cases := []struct {
		start Node
		end   Node
		path  NodePath
		error error
	}{
		{start: n1, end: n2, path: NodePath{n1, n2}},
		{start: n6, end: n7, path: NodePath{n6, n7}},
		{start: n1, end: n6, error: ErrPathNotFound},
		{start: n7, end: n6, error: ErrPathNotFound},
		{start: n1, end: n4, path: NodePath{n1, n2, n4}},
		{start: n1, end: n5, path: NodePath{n1, n2, n4, n5}},
		{start: n1, end: n1, path: NodePath{n1, n2, n1}},
	}

	for _, c := range cases {
		got, err := graph.ShortestPath(c.start, c.end)
		if err != c.error {
			t.Errorf("FAIL: (%v -> %v) got error %v; expected %v", c.start, c.end, err, c.error)
		} else if !got.Equal(&c.path) {
			t.Errorf("FAIL: (%v -> %v) got path %v; expected %v", c.start, c.end, got, c.path)
		} else {
			t.Logf("PASS: (%v -> %v)", c.start, c.end)
		}
	}
}
