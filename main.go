package main

import (
	"flag"
	"github.com/landmaj/WikedGame/graph"
	"github.com/landmaj/WikedGame/parser"
	"log"
)

var dbFile string
var xmlFile string

func init() {
	flag.StringVar(&dbFile, "db", "", "Bolt DB filename")
	flag.StringVar(&xmlFile, "xml", "", "[optional] XML file to parse")
	flag.Parse()
}

func main() {
	if dbFile == "" {
		log.Fatal("'-db' flag required")
	}
	storage := graph.BoltStorage{}
	if err := storage.Init(dbFile); err != nil {
		log.Fatal(err)
	}

	if xmlFile != "" {
		log.Println("Parsing XML:", xmlFile)
		parser.ParseXML(&storage, xmlFile)
	}
}
