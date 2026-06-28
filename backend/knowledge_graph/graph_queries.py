# ============================================
# ENTITY QUERIES
# ============================================

CREATE_ENTITY = """
MERGE (e:Entity {
    name: $name,
    type: $type
})
"""


# ============================================
# RELATIONSHIP QUERIES
# ============================================

CREATE_RELATION = """
MATCH (a:Entity {name:$source})
MATCH (b:Entity {name:$target})

MERGE (a)-[r:RELATION {
    type:$relation
}]->(b)
"""


# ============================================
# GRAPH RETRIEVAL
# ============================================

GET_ENTITY = """
MATCH (e:Entity {name:$name})
RETURN e
"""


GET_NEIGHBORS = """
MATCH (e:Entity {name:$name})-[r]-(n)

RETURN
e,
r,
n
"""


SEARCH_ENTITIES = """
MATCH (e:Entity)

WHERE
toLower(e.name)
CONTAINS
toLower($query)

RETURN e

LIMIT 10
"""


GET_SUBGRAPH = """
MATCH (e:Entity {name:$name})-[*1..2]-(n)

RETURN e,n
"""