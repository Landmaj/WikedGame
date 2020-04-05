package graph

import (
	"errors"
)

var (
	ErrPathNotFound  = errors.New("path not found")
	ErrNodeNotFound  = errors.New("node not found")
	ErrBackendFailed = errors.New("backend failed")
)

type (
	Storage interface {
		GetNode(uint32) (Node, error)
	}
	Graph struct {
		backend Storage
	}
)

func (g *Graph) ShortestPath(a, b Node) (NodePath, error) {
	queue := []uint32{a.id}
	previouslySeen := make(map[uint32]uint32)

	for len(queue) != 0 {
		currentNode, err := g.backend.GetNode(queue[0])
		if err == ErrNodeNotFound {
			continue
		} else if err != nil {
			return NodePath{}, ErrBackendFailed
		}

		queue = queue[1:]

		for id := range currentNode.connections {
			if _, ok := (previouslySeen)[id]; ok {
				continue
			}
			queue = append(queue, id)
			previouslySeen[id] = currentNode.id
		}

		if currentNode.connections.contains(b.id) {
			path := NodePath{b}
			for id := previouslySeen[b.id]; id != a.id; id = previouslySeen[id] {
				node, _ := g.backend.GetNode(id)
				path = append(path, node)
			}
			path = append(path, a)
			path.reverse()
			return path, nil
		}
	}
	return NodePath{}, ErrPathNotFound
}
