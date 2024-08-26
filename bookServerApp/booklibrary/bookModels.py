from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredNode, StringProperty, Relationship, RelationshipTo, RelationshipFrom

class Author(StructuredNode) :
    name = StringProperty(UniqueIdProperty=True, required=True)
    orderedName=StringProperty()
    similar_with = Relationship('Author', 'SIMILAR_WITH')
    books = RelationshipFrom('Book', 'AUTHORED_BY')

class Book(StructuredNode):
    title = StringProperty(unique_index=True, required=True)  # 标题作为唯一标识
    orderedTitle = StringProperty()
    authors = RelationshipTo(Author, 'AUTHORED_BY')