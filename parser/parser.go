package parser

import (
	"bufio"
	"fmt"
	"github.com/dsnet/compress/bzip2"
	"github.com/landmaj/WikedGame/graph"
	xmlparser "github.com/tamerh/xml-stream-parser"
	"log"
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
	{
		fmt.Println("First pass...")
		parser, file := newXMLParser(filename, pageTag)
		defer file.Close()
		generateTitleToID(storage, parser)
	}
	{
		fmt.Println("Second pass...")
		parser, file := newXMLParser(filename, pageTag)
		defer file.Close()
		generateNodes(storage, parser)
	}
}

func newXMLParser(filename string, loopElements ...string) (*xmlparser.XMLParser, *os.File) {
	f, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	r, err := bzip2.NewReader(f, nil)
	if err != nil {
		log.Fatal(err)
	}
	br := bufio.NewReaderSize(r, 65536)
	return xmlparser.NewXMLParser(br, loopElements...), f
}

func generateTitleToID(st graph.Storage, parser *xmlparser.XMLParser) {
	ch := trackProgress()
	parser.SkipElements([]string{revisionTag, redirectTag})
	wg := sync.WaitGroup{}
	for xml := range parser.Stream() {
		ch <- parser.TotalReadSize
		if isMainNamespace(xml) {
			wg.Add(1)
			go func(xml *xmlparser.XMLElement, wg *sync.WaitGroup) {
				defer wg.Done()
				err := st.SetTitleToID(xmlToTitle(xml), xmlToID(xml))
				if err != nil {
					log.Fatal(err)
				}
			}(xml, &wg)
		}
	}
	close(ch)
	wg.Wait()
}

func generateNodes(storage graph.Storage, parser *xmlparser.XMLParser) {
	ch := trackProgress()
	wg := sync.WaitGroup{}
	for xml := range parser.Stream() {
		ch <- parser.TotalReadSize
		wg.Add(1)
		go func(xml *xmlparser.XMLElement, wg *sync.WaitGroup) {
			defer wg.Done()
			if isMainNamespace(xml) {
				title := xmlToTitle(xml)
				id := xmlToID(xml)
				var connections []uint32
				if redirectTo, ok := isRedirect(xml); ok {
					redirectID, err := storage.GetID(redirectTo)
					if err == graph.ErrNodeNotFound {
						connections = []uint32{}
					} else if err != nil {
						log.Fatal(err)
					} else {
						connections = []uint32{redirectID}
					}
				} else {
					links := extractLinks(xmlToText(xml))
					for link := range links {
						linkID, err := storage.GetID(link.Target)
						if err == graph.ErrNodeNotFound {
							continue
						} else if err != nil {
							log.Fatal(err)
						} else {
							connections = append(connections, linkID)
						}
					}
				}
				node := graph.NewNode(id, title, connections...)
				err := storage.SetNode(node)
				if err != nil {
					log.Fatal(err)
				}
			}
		}(xml, &wg)
	}
	close(ch)
	wg.Wait()
}

func isMainNamespace(xml *xmlparser.XMLElement) bool {
	ns, _ := strconv.Atoi(xml.Childs[nsTag][0].InnerText)
	return ns == 0
}

func isRedirect(xml *xmlparser.XMLElement) (string, bool) {
	if redirect := xml.Childs[redirectTag]; len(redirect) > 0 {
		return redirect[0].Attrs[titleTag], true
	}
	return "", false
}

func xmlToTitle(xml *xmlparser.XMLElement) string {
	return xml.Childs[titleTag][0].InnerText
}

func xmlToID(xml *xmlparser.XMLElement) uint32 {
	id, err := strconv.Atoi(xml.Childs[idTag][0].InnerText)
	if err != nil {
		log.Fatal(err)
	}
	return uint32(id)
}

func xmlToText(xml *xmlparser.XMLElement) string {
	return xml.Childs[revisionTag][0].Childs[textTag][0].InnerText
}

func trackProgress() chan<- uint64 {
	ch := make(chan uint64)
	go func() {
		started := time.Now()
		var previous int64
		for in := range ch {
			elapsed := int64(time.Since(started).Seconds())
			if elapsed > previous {
				mBytesPerSecond := int64(in) / elapsed / (1024 * 1024)
				fmt.Printf("\r%ds elapsed, %d mB/s", elapsed, mBytesPerSecond)
				previous = elapsed
			}
		}
		fmt.Println()
	}()
	return ch
}
