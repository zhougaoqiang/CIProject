from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredRel, StructuredNode, StringProperty, IntegerProperty, Relationship, RelationshipTo, RelationshipFrom, UniqueIdProperty, FloatProperty

class Author(StructuredNode) :
    name = StringProperty(UniqueIdProperty=True, required=True)
    orderedName=StringProperty()
    similar_with = Relationship('Author', 'SIMILAR_WITH')
    books = RelationshipFrom('Book', 'AUTHORED_BY')

# class Category(StructuredNode) :
#     name = StringProperty(unique_index=True, required=True)
#     books = RelationshipFrom('Book', 'HAS_CATEGORY')
    
# class Publisher(StructuredNode) :
#     name = StringProperty(unique_index=True, required=True)
#     books = RelationshipFrom('Book', 'PUBLISHED_BY')

# class PublishYear(StructuredNode) :
#     name = IntegerProperty(unique_index=True, required=True)
#     books = RelationshipFrom('Book', 'PUBLISHED_YEAR')

# class Rating(StructuredNode) :
#     name = IntegerProperty(unique_index=True, required=True)
#     actualRating = FloatProperty()

class Book(StructuredNode):
    title = StringProperty(unique_index=True, required=True)  # 标题作为唯一标识
    orderedTitle = StringProperty()
    # description = StringProperty()
    # image = StringProperty()
    # previewLink = StringProperty()
    # infoLink = StringProperty()
    # ratingsCount = FloatProperty()
    # publishDate = StringProperty()
    authors = RelationshipTo(Author, 'AUTHORED_BY')
    # categories = RelationshipTo(Category, 'HAS_CATEGORY')
    # publisher = RelationshipTo(Publisher, 'PUBLISHED_BY')
    # publishYear = RelationshipTo(PublishYear, 'PUBLISHED_YEAR')