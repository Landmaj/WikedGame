package graph

import (
	"errors"
)

var (
	ErrPathNotFound  = errors.New("path not found")
	ErrBackendFailed = errors.New("backend failed")
)

type (
	Graph struct{ Storage }
)

func (g *Graph) ShortestPath(a, b Node) (NodePath, error) {
	queue := []uint32{a.Id}
	previouslySeen := make(map[uint32]uint32)

	for len(queue) != 0 {
		currentNode, err := g.GetNode(queue[0])
		if err == ErrNodeNotFound {
			continue
		} else if err != nil {
			return NodePath{}, ErrBackendFailed
		}

		queue = queue[1:]

		for id := range currentNode.Connections {
			if _, ok := (previouslySeen)[id]; ok {
				continue
			}
			queue = append(queue, id)
			previouslySeen[id] = currentNode.Id
		}

		if currentNode.Connections.contains(b.Id) {
			path := NodePath{b}
			for id := previouslySeen[b.Id]; id != a.Id; id = previouslySeen[id] {
				node, _ := g.GetNode(id)
				path = append(path, node)
			}
			path = append(path, a)
			path.reverse()
			return path, nil
		}
	}
	return NodePath{}, ErrPathNotFound
}
