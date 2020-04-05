package graph

import (
	"fmt"
	"github.com/golang/protobuf/proto"
	"github.com/landmaj/WikedGame/pb"
)

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

func (n *Node) Equal(other Node) bool {
	if n.id != other.id ||
		n.title != other.title ||
		!n.connections.equal(&other.connections) {
		return false
	}
	return true
}

func (n *Node) String() string {
	return fmt.Sprint(n.title)
}

func (n *Node) ToBytes() []byte {
	pbNode := pb.Node{
		Id:          n.id,
		Title:       n.title,
		Connections: n.connections.toSlice(),
	}
	if msg, err := proto.Marshal(&pbNode); err != nil {
		panic(err)
	} else {
		return msg
	}
}

func (n *Node) FromBytes(b []byte) *Node {
	pbNode := &pb.Node{}
	if err := proto.Unmarshal(b, pbNode); err != nil {
		panic(err)
	}
	n.id = pbNode.Id
	n.title = pbNode.Title
	n.connections = newSet(pbNode.Connections...)
	return n
}
