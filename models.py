from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, UniqueIdProperty, DateProperty, ArrayProperty, FloatProperty

    
class Author(StructuredNode) :
    name = StringProperty(UniqueIdProperty=True, required=True)
    similar_with = RelationshipTo('Author', 'SIMILAR_WITH')

class Category(StructuredNode) :
    name = StringProperty(unique_index=True, required=True)
    
class Publisher(StructuredNode) :
    name = StringProperty(unique_index=True, required=True)

class PublishYear(StructuredNode) :
    name = IntegerProperty(unique_index=True, required=True)
    actualDate = StringProperty()

# class Rating(StructuredNode) :
#     name = IntegerProperty(unique_index=True, required=True)
#     actualRating = FloatProperty()

class Book(StructuredNode):
    title = StringProperty(unique_index=True, required=True)  # 标题作为唯一标识
    description = StringProperty()
    image = StringProperty()
    previewLink = StringProperty()
    infoLink = StringProperty()
    ratingsCount = FloatProperty()
    authors = RelationshipTo(Author, 'AUTHORED_BY')
    categories = RelationshipTo(Category, 'HAS_CATEGORY')
    publisher = RelationshipTo(Publisher, 'PUBLISHED_BY')
    publishYear = RelationshipTo(PublishYear, 'PUBLISHED_YEAR')
