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
	SetTitleToID(title string, id uint32) error
	SetNode(Node) error
	GetID(title string) (uint32, error)
	GetNode(uint32) (Node, error)
}

// RAM

type ramStorage map[uint32]Node

func (s *ramStorage) SetTitleToID(title string, id uint32) error {
	return nil
}

func (s *ramStorage) SetNode(n Node) error {
	(*s)[n.Id] = n
	return nil
}

func (s *ramStorage) GetID(title string) (uint32, error) {
	for _, v := range *s {
		if v.Title == title {
			return v.Id, nil
		}
	}
	return 0, ErrNodeNotFound
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
	nodesBucket     string
	titleToIDBucket string
}

func (db *BoltStorage) Init(filename string) error {
	var err error
	db.DB, err = bolt.Open(filename, 0600, &bolt.Options{Timeout: 1 * time.Second})
	if err != nil {
		log.Fatal(err)
	}

	db.nodesBucket = "nodes"
	if err := db.Update(func(tx *bolt.Tx) error {
		_, err := tx.CreateBucketIfNotExists([]byte(db.nodesBucket))
		return err
	}); err != nil {
		return err
	}
	db.titleToIDBucket = "titleToIDBucket"
	if err := db.Update(func(tx *bolt.Tx) error {
		_, err := tx.CreateBucketIfNotExists([]byte(db.titleToIDBucket))
		return err
	}); err != nil {
		return err
	}
	return nil
}

func (db *BoltStorage) SetTitleToID(title string, id uint32) error {
	err := db.Batch(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(db.titleToIDBucket))
		err := b.Put([]byte(title), idToBytes(id))
		return err
	})
	return err
}

func (db *BoltStorage) SetNode(n Node) error {
	err := db.Batch(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(db.nodesBucket))
		err := b.Put(idToBytes(n.Id), n.ToBytes())
		return err
	})
	return err
}
func (db *BoltStorage) GetID(title string) (uint32, error) {
	var v []byte
	if err := db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(db.titleToIDBucket))
		v = b.Get([]byte(title))
		return nil
	}); err != nil {
		return 0, err
	}
	if v == nil {
		return 0, ErrNodeNotFound
	}
	return bytesToID(v), nil
}

func (db *BoltStorage) GetNode(id uint32) (Node, error) {
	var v []byte
	if err := db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(db.nodesBucket))
		v = b.Get(idToBytes(id))
		return nil
	}); err != nil {
		return Node{}, err
	}
	if v == nil {
		return Node{}, ErrNodeNotFound
	}
	node := Node{}
	node.FromBytes(v)
	return node, nil
}

func idToBytes(id uint32) []byte {
	bytes := make([]byte, 4)
	binary.LittleEndian.PutUint32(bytes, id)
	return bytes
}

func bytesToID(bytes []byte) uint32 {
	return binary.LittleEndian.Uint32(bytes)
}
