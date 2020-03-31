package graph

import (
	"fmt"
	mapset "github.com/deckarep/golang-set"
	"testing"
)

type inMemoryStorage map[uint32]Node

func (s *inMemoryStorage) GetNode(i uint32) *Node {
	if n, ok := (*s)[i]; ok {
		return &n
	}
	return nil
}

func equal(a, b []*Node) bool {
	if len(a) != len(b) {
		return false
	}
	for i := 0; i < len(a); i++ {
		if *a[i] != *b[i] {
			return false
		}
	}
	return true
}

func (n *Node) String() string {
	return fmt.Sprint(n.id)
}

func TestShortestPath(t *testing.T) {
	n1 := Node{
		id:          1,
		title:       "one",
		connections: mapset.NewThreadUnsafeSetFromSlice([]interface{}{uint32(2), uint32(3)}),
	}
	n2 := Node{
		id:          2,
		title:       "two",
		connections: mapset.NewThreadUnsafeSetFromSlice([]interface{}{uint32(1), uint32(4)}),
	}
	n3 := Node{
		id:          3,
		title:       "three",
		connections: mapset.NewThreadUnsafeSetFromSlice([]interface{}{uint32(2)}),
	}
	n4 := Node{
		id:          4,
		title:       "four",
		connections: mapset.NewThreadUnsafeSetFromSlice([]interface{}{uint32(5)}),
	}
	n5 := Node{
		id:          5,
		title:       "five",
		connections: mapset.NewThreadUnsafeSetFromSlice([]interface{}{uint32(2)}),
	}
	n6 := Node{
		id:          6,
		title:       "six",
		connections: mapset.NewThreadUnsafeSetFromSlice([]interface{}{uint32(7)}),
	}
	n7 := Node{
		id:          7,
		title:       "seven",
		connections: mapset.NewThreadUnsafeSetFromSlice([]interface{}{}),
	}
	storage := inMemoryStorage{1: n1, 2: n2, 3: n3, 4: n4, 5: n5, 6: n6, 7: n7}
	graph := Graph{backend: &storage}

	cases := []struct {
		start *Node
		end   *Node
		path  []*Node
		error error
	}{
		{start: &n1, end: &n2, path: []*Node{&n1, &n2}},
		{start: &n6, end: &n7, path: []*Node{&n6, &n7}},
		{start: &n1, end: &n6, error: ErrPathNotFound},
		{start: &n7, end: &n6, error: ErrPathNotFound},
		{start: &n1, end: &n4, path: []*Node{&n1, &n2, &n4}},
		{start: &n1, end: &n5, path: []*Node{&n1, &n2, &n4, &n5}},
		{start: &n1, end: &n1, path: []*Node{&n1, &n2, &n1}},
	}

	for _, c := range cases {
		got, err := graph.ShortestPath(c.start, c.end)
		if err != c.error {
			t.Errorf("FAIL: (%v -> %v) got error %v; expected %v", c.start, c.end, err, c.error)
		} else if !equal(got, c.path) {
			t.Errorf("FAIL: (%v -> %v) got path %v; expected %v", c.start, c.end, got, c.path)
		} else {
			t.Logf("PASS: (%v -> %v)", c.start, c.end)
		}
	}
}
