WickedGame
==========

**This is still an early stage of the project!**

To import data into Neo4j:
--------------------------

.. code:: Bash

    neo4j-admin import \
    --mode csv \
    --database graph.db \
    --ignore-missing-nodes \
    --delimiter "\t" \
    --nodes="/path/to/neo4j/import/node.csv" \
    --relationships="/path/to/neo4j/import/relationship.csv"

Cypher queries
--------------

1. Shortest path between nodes:

.. code:: Cypher

    MATCH (s:Page {title: "FROM"}), (e:Page {title: "TO"}), p=shortestPath((s)-[*]->(e))
    WITH p
    WHERE length(p) > 1
    RETURN p, length(p)

2. Relationships to a node:

.. code:: Cypher

    MATCH (n)<-[r]-() WHERE n.title = 'TO' RETURN COUNT(r)

3. Relationship from a node:

.. code:: Cypher

    MATCH (n)-[r]->() WHERE n.title = 'FROM' RETURN COUNT(r)
