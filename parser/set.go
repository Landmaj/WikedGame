package parser

type set map[Link]struct{}

func (s *set) add(l Link) {
	(*s)[l] = struct{}{}
}
