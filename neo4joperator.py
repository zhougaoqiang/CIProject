from neo4j import GraphDatabase
class Neo4jOperator :
    def __init__(self, uri, user, password) :
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def find_node_by_name(self, node_type, name):
        with self.driver.session() as session :
            result = session.read_transaction(self._find_and_return_node, node_type, name)
            return result
        
    @staticmethod
    def _find_and_return_node(tx, node_type, name) :
        query = (
            f"MATCH (n:{node_type}) WHERE n.name = $name RETURN n"
        )
        result = tx.run(query, name=name)
        return [record["n"] for record in result]
    
    def delete_node_by_name(self, node_type, name) :
        with self.driver.session() as session :
            result = session.write_transaction(self._delete_node, node_type, name)
            return result
    
    @staticmethod
    def _delete_node(tx, node_type, name) :
        query = (
            f"MATCH (n:{node_type} WHERE n.name = $name DELETE n)"
        )
        result = tx.run(query, name=name)
        return result.summary().counters.nodes_deleted
    
    def find_node_and_relationships_by_name(self, node_type, name) :
        with self.driver.session() as session :
            result = session.read_transaction(self._find_and_return_node_relationships, node_type, name)
            return result
        
    def _find_and_return_node_and_relationships(tx, node_type, name):
        query = (
            f"""
            MATCH (n:{node_type})-[r]->(m)
            WHERE n.name = $name
            RETURN n, type(r) as relationship_type, r, m
            """
        )
        result = tx.run(query, name=name)
        relationships = []
        for record in result:
            relationships.append({
                "node": record["n"],
                "relationship_type": record["relationship_type"],
                "relationship_properties": dict(record["r"]),
                "connected_node": record["m"]
             })
        return relationships