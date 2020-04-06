package graph

import (
	"encoding/binary"
	"errors"
	"github.com/boltdb/bolt"
	"log"
	"time"
)

var ErrNodeNotFound = errors.New("node not found")

type Storage interface {
	GetNode(uint32) (Node, error)
	SetNode(Node)
}

// RAM

type ramStorage map[uint32]Node

func (s *ramStorage) SetNode(n Node) {
	(*s)[n.Id] = n
}

func (s *ramStorage) GetNode(i uint32) (Node, error) {
	if n, ok := (*s)[i]; ok {
		return n, nil
	}
	return Node{}, ErrNodeNotFound
}

// BOLT

type BoltStorage struct {
	*bolt.DB
	bucket string
}

func (db *BoltStorage) Init(filename string) {
	var err error
	db.DB, err = bolt.Open(filename, 0600, &bolt.Options{Timeout: 1 * time.Second})
	if err != nil {
		log.Fatal(err)
	}

	db.bucket = "nodes"
	if err := db.Update(func(tx *bolt.Tx) error {
		_, err := tx.CreateBucketIfNotExists([]byte(db.bucket))
		return err
	}); err != nil {
		log.Fatal(err)
	}
}

func (db *BoltStorage) SetNode(n Node) {
	id := make([]byte, 4)
	binary.LittleEndian.PutUint32(id, n.Id)
	if err := db.Batch(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(db.bucket))
		err := b.Put(id, n.ToBytes())
		return err
	}); err != nil {
		panic(err)
	}
}

func (db *BoltStorage) GetNode(i uint32) (Node, error) {
	id := make([]byte, 4)
	binary.LittleEndian.PutUint32(id, i)
	var v []byte
	if err := db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(db.bucket))
		v = b.Get(id)
		return nil
	}); err != nil {
		panic(err)
	}
	if v == nil {
		return Node{}, ErrNodeNotFound
	}
	node := Node{}
	node.FromBytes(v)
	return node, nil
}
