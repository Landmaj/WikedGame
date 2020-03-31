package graph

import (
	"errors"
	mapset "github.com/deckarep/golang-set"
)

var ErrPathNotFound = errors.New("path not found")

type Storage interface {
	GetNode(uint32) *Node
}

type Graph struct {
	backend Storage
}

type Node struct {
	id          uint32
	title       string
	connections mapset.Set
}

type queue []uint32

func (q *queue) append(s mapset.Set) {
	for _, i := range s.ToSlice() {
		*q = append(*q, i.(uint32))
	}
}

func markCompleted(n *Node, q *queue, p *map[uint32]uint32) {
	*q = (*q)[1:]
	for _, i := range n.connections.ToSlice() {
		i := i.(uint32)
		if _, ok := (*p)[i]; ok {
			continue
		}
		*q = append(*q, i)
		(*p)[i] = n.id
	}
}

func retracePath(a, b *Node, p *map[uint32]uint32, g *Graph) (path []*Node) {
	path = append(path, a)
	for i := (*p)[a.id]; i != b.id; i = (*p)[i] {
		path = append(path, g.backend.GetNode(i))
	}
	path = append(path, b)
	for left, right := 0, len(path)-1; left < right; left, right = left+1, right-1 {
		path[left], path[right] = path[right], path[left]
	}
	return
}

func (g *Graph) ShortestPath(a, b *Node) ([]*Node, error) {
	q := queue{a.id}
	p := make(map[uint32]uint32)
	for len(q) != 0 {
		n := g.backend.GetNode(q[0])
		if n == nil {
			continue
		}
		markCompleted(n, &q, &p)
		if n.connections.Contains(b.id) {
			return retracePath(b, a, &p, g), nil
		}
	}
	return []*Node{}, ErrPathNotFound
}
