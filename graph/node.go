package graph

import "fmt"

type Node struct {
	id          uint32
	title       string
	connections set
}

func NewNode(id uint32, title string, connections ...uint32) Node {
	return Node{
		id:          id,
		title:       title,
		connections: newSet(connections...),
	}
}

func (n Node) Equal(other Node) bool {
	if n.id != other.id ||
		n.title != other.title ||
		!n.connections.equal(&other.connections) {
		return false
	}
	return true
}

func (n Node) String() string {
	return fmt.Sprint(n.title)
}
