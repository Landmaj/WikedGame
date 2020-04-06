package parser

import (
	"bufio"
	"fmt"
	"github.com/dsnet/compress/bzip2"
	"github.com/landmaj/WikedGame/graph"
	xmlparser "github.com/tamerh/xml-stream-parser"
	"os"
	"strconv"
	"sync"
	"time"
)

const (
	idTag       = "id"
	nsTag       = "ns"
	pageTag     = "page"
	redirectTag = "redirect"
	revisionTag = "revision"
	textTag     = "text"
	titleTag    = "title"
)

func ParseXML(storage graph.Storage, filename string) {
	idMap := make(map[string]uint32)
	{
		fmt.Println("First pass...")
		p, f := newXMLParser(filename, pageTag)
		defer f.Close()
		idMap = generateTitleToID(p)
	}
	{
		fmt.Println("Second pass...")
		p, f := newXMLParser(filename, pageTag)
		defer f.Close()
		generateNodes(p, storage, &idMap)
	}
}

func newXMLParser(filename string, loopElements ...string) (*xmlparser.XMLParser, *os.File) {
	f, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	r, err := bzip2.NewReader(f, nil)
	if err != nil {
		panic(err)
	}
	br := bufio.NewReaderSize(r, 65536)
	return xmlparser.NewXMLParser(br, loopElements...), f
}

func generateTitleToID(parser *xmlparser.XMLParser) map[string]uint32 {
	output := make(map[string]uint32)
	parser.SkipElements([]string{revisionTag, redirectTag})
	started := time.Now()
	var previous int64
	for xml := range parser.Stream() {
		elapsed := int64(time.Since(started).Seconds())
		if elapsed > previous {
			mBytesPerSecond := int64(parser.TotalReadSize) / elapsed / (1024 * 1024)
			fmt.Printf("\r%ds elapsed, %d mB/s", elapsed, mBytesPerSecond)
			previous = elapsed
		}
		if isMainNamespace(xml) {
			output[getTitle(xml)] = getID(xml)
		}
	}
	fmt.Println()
	return output
}

func generateNodes(pr *xmlparser.XMLParser, st graph.Storage, idMap *map[string]uint32) {
	wgSender := sync.WaitGroup{}
	started := time.Now()
	var previous int64
	for xml := range pr.Stream() {
		elapsed := int64(time.Since(started).Seconds())
		if elapsed > previous {
			mBytesPerSecond := int64(pr.TotalReadSize) / elapsed / (1024 * 1024)
			fmt.Printf("\r%ds elapsed, %d mB/s", elapsed, mBytesPerSecond)
			previous = elapsed
		}
		if isMainNamespace(xml) {
			title := getTitle(xml)
			id := getID(xml)
			if ok, redirect := isRedirect(xml); ok {
				if redirectID, ok := (*idMap)[redirect]; ok {
					node := graph.NewNode(id, title, redirectID)
					saveNode(&node, st, &wgSender)
				}
			} else {
				links := extractLinks(getArticleText(xml))
				var connections []uint32
				for link := range links {
					if linkId, ok := (*idMap)[link.Target]; ok {
						connections = append(connections, linkId)
					}
					node := graph.NewNode(id, title, connections...)
					saveNode(&node, st, &wgSender)
				}
			}
		}
	}
	fmt.Println()
	wgSender.Wait()
}

func isMainNamespace(xml *xmlparser.XMLElement) bool {
	ns, _ := strconv.Atoi(xml.Childs[nsTag][0].InnerText)
	return ns == 0
}

func isRedirect(xml *xmlparser.XMLElement) (bool, string) {
	if redirect := xml.Childs[redirectTag]; len(redirect) > 0 {
		return true, redirect[0].Attrs[titleTag]
	}
	return false, ""
}

func getTitle(xml *xmlparser.XMLElement) string {
	return xml.Childs[titleTag][0].InnerText
}

func getID(xml *xmlparser.XMLElement) uint32 {
	id, err := strconv.Atoi(xml.Childs[idTag][0].InnerText)
	if err != nil {
		panic(err)
	}
	return uint32(id)
}

func getArticleText(xml *xmlparser.XMLElement) string {
	return xml.Childs[revisionTag][0].Childs[textTag][0].InnerText
}

func saveNode(n *graph.Node, st graph.Storage, wg *sync.WaitGroup) {
	wg.Add(1)
	go func(n *graph.Node, st graph.Storage, wg *sync.WaitGroup) {
		defer wg.Done()
		st.SetNode(*n)
	}(n, st, wg)
}
