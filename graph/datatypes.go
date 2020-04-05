package graph

import "reflect"

// SET

type set map[uint32]struct{}

func newSet(ids ...uint32) set {
	output := make(set)
	for _, v := range ids {
		output[v] = struct{}{}
	}
	return output
}

func (s *set) add(i uint32) {
	(*s)[i] = struct{}{}
}

func (s *set) contains(i uint32) bool {
	_, ok := (*s)[i]
	return ok
}

func (s *set) equal(other *set) bool {
	return reflect.DeepEqual(*s, *other)
}

// PATH

type NodePath []Node

func (np *NodePath) reverse() *NodePath {
	for l, r := 0, len(*np)-1; l < r; l, r = l+1, r-1 {
		(*np)[l], (*np)[r] = (*np)[r], (*np)[l]
	}
	return np
}

func (np *NodePath) Equal(other *NodePath) bool {
	if len(*np) != len(*other) {
		return false
	}
	for i, v := range *np {
		if !v.Equal((*other)[i]) {
			return false
		}
	}
	return true
}
