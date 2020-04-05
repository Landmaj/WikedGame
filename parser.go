package main

//
// import (
// 	"bufio"
// 	"fmt"
// 	"github.com/dsnet/compress/bzip2"
// 	"github.com/landmaj/WikedGame/graph"
// 	xmlparser "github.com/tamerh/xml-stream-parser"
// 	"os"
// 	"time"
// )
//
// func parseXMLDump(s *graph.Storage, filename string) {
// 	f, err := os.Open(filename)
// 	if err != nil {
// 		panic(err)
// 	}
// 	r, err := bzip2.NewReader(f, nil)
// 	if err != nil {
// 		panic(err)
// 	}
// 	br := bufio.NewReaderSize(r, 65536)
// 	parser := xmlparser.NewXMLParser(br, "page")
// 	started := time.Now()
// 	var previous int64
// 	for xml := range parser.Stream() {
// 		go parseElement(s, xml)
// 		elapsed := int64(time.Since(started).Seconds())
// 		if elapsed > previous {
// 			mBytesPerSecond := int64(parser.TotalReadSize) / elapsed / (1024 * 1024)
// 			fmt.Printf("\r%ds elapsed, %d mB/s", elapsed, mBytesPerSecond)
// 			previous = elapsed
// 		}
// 	}
// 	fmt.Println()
// }
//
// func parseElement(s *graph.Storage, element *xmlparser.XMLElement) {
//
// }
