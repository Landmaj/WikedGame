// Source: https://github.com/semanticize/dumpparser/blob/master/dumpparser/wikidump/wikisyntax.go

package parser

import (
	"regexp"
	"strings"
	"unicode"
	"unicode/utf8"
)

type Link struct {
	Anchor, Target string
}

var (
	linkRE     = regexp.MustCompile(`(\w*)\[\[([^]]+)\]\](\w*)`)
	whitespace = regexp.MustCompile(`[\s_]+`)
)

func normSpace(s string) string {
	s = whitespace.ReplaceAllLiteralString(s, " ")
	return strings.TrimSpace(s)
}

func extractLinks(s string) set {
	output := set{}
	for _, candidate := range linkRE.FindAllStringSubmatch(s, -1) {
		before, l, after := candidate[1], candidate[2], candidate[3]

		var target, anchor string
		if pipe := strings.IndexByte(l, '|'); pipe != -1 {
			target, anchor = l[:pipe], l[pipe+1:]
		} else {
			target = l
			anchor = l
		}

		// If the anchor contains a colon, assume it's a file or category link.
		// XXX Maybe skip matches for `:\s`? Proper solution would parse the
		// dump to find non-main namespace prefixes.
		if strings.IndexByte(target, ':') != -1 {
			continue
		}

		// Remove section links.
		if hash := strings.IndexByte(target, '#'); hash == 0 {
			continue
		} else if hash != -1 {
			target = target[:hash]
		}

		// Normalize to the format used in <redirect> elements:
		// uppercase first character, spaces instead of underscores.
		target = normSpace(target)
		first, size := utf8.DecodeRuneInString(target)
		// XXX Upper case or title case? Should look up the difference...
		if unicode.IsLower(first) {
			target = string(unicode.ToUpper(first)) + target[size:]
		}

		anchor = before + anchor + after
		output.add(Link{anchor, target})
	}
	return output
}
