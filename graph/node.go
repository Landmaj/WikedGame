package graph

import (
	"fmt"
	"github.com/golang/protobuf/proto"
	"github.com/landmaj/WikedGame/pb"
)

type Node struct {
	Id          uint32
	Title       string
	Connections set
}

func NewNode(id uint32, title string, connections ...uint32) Node {
	return Node{
		Id:          id,
		Title:       title,
		Connections: newSet(connections...),
	}
}

func (n *Node) Equal(other Node) bool {
	if n.Id != other.Id ||
		n.Title != other.Title ||
		!n.Connections.equal(&other.Connections) {
		return false
	}
	return true
}

func (n *Node) String() string {
	return fmt.Sprint(n.Title)
}

func (n *Node) ToBytes() []byte {
	pbNode := pb.Node{
		Id:          n.Id,
		Title:       n.Title,
		Connections: n.Connections.toSlice(),
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
	n.Id = pbNode.Id
	n.Title = pbNode.Title
	n.Connections = newSet(pbNode.Connections...)
	return n
}
