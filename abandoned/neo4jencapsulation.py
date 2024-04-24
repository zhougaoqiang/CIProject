from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class BookNeo4j:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def executeCypher(self, cypher, parameters=None):
        try:
            with self.driver.session() as session:
                result = session.run(cypher, parameters=parameters)
                return result.records if result else result.single()
        except ServiceUnavailable as e:
            self.logger.error("Service unavailable error encountered: ", exc_info=e)
            raise
        except Exception as e:
            self.logger.error("An error occurred while executing Cypher query:", exc_info=e)
            raise


        
        """
        # Create a new "Book" node with unique property "bookId":
        new_book = book_neo4j.create_or_update_node(
        label_name="Book",
        properties={"bookId": 123, "title": "The Hitchhiker's Guide to the Galaxy"},
        on_create="SET book.addedOn = timestamp()"  # Set creation timestamp
        )

        if new_book:
            print(f"New book created with ID: {new_book['id']}")  # Access properties using dictionary-like access

        # Update an existing "Book" node with the same "bookId":
        updated_book = book_neo4j.create_or_update_node(
            label_name="Book",
            properties={"bookId": 123, "publisher": "Pan Books"},
        on_match="SET book.lastUpdated = timestamp()"  
        """
        
    def createUpdateNode(self, labelname, properties, onCreate=None, onMatch=None):
        unique_property, unique_value = self._get_unique_property(properties)
        cypher = f"""
        WITH {unique_property}, {unique_value}
        OPTIONAL MATCH (node:{labelname})
        WHERE node.{unique_property} = {unique_value}
        WITH node, {unique_value} AS existing_value
        WITH CASE WHEN node IS NULL THEN {unique_value} ELSE existing_value END AS actual_value
        MERGE (node:{labelname})
        ON CREATE SET node.{unique_property} = actual_value
        {onCreate}
        WITH node
        WHERE node.{unique_property} = actual_value  <<-- Ensures created node is returned
        RETURN node
        """
        result = self.executeCypher(cypher)
        return result.single() if result else None
    
    
    
    def createRelationship(self, startLabel, endLabel, relationshipType, properties=None):
        cypher = f"""
            MATCH (start:{startLabel}), (end:{endLabel})
            WHERE start.[unique_property_start] = {unique_value_start}  <<-- Replace with actual property and value
            AND end.[unique_property_end] = {unique_value_end}        <<-- Replace with actual property and value
            CREATE (start)-[:{relationshipType}]->(end)
            {f'SET rel.{", ".join([f"{k} = {v}" for k, v in (properties or {}).items()])}' if properties else ''}
            RETURN rel
        """
        result = self.executeCypher(cypher)
        return result.single()