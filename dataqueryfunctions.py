from models import Book, Author, Category, Publisher, PublishYear

class DataQuery :
    def __init__(self) :
        print("Create DataQuery")
    
    def getBookNode(self, book_title) :
        try:
            rtn = Book.nodes.get(title=book_title)
            print(rtn)
            return rtn
        except Exception as e:
            print(f'node not exist Book : {book_title}')
            return None
        
    @staticmethod
    def _getNode(nodeName, idValue) :
        try:
            rtn = nodeName.nodes.get(name=idValue)
            print(rtn)
            return rtn
        except Exception as e:
            print(f'node not exist {nodeName}={idValue}')
            return None
    
    def getAuthorNode(self, authorName) :
        return DataQuery._getNode(Author, authorName)
    
    def getCategoryNode(self, categoryName) :
        return DataQuery._getNode(Category, categoryName)
    
    def getPublisherNode(self, publisherName) :
        return DataQuery._getNode(Publisher, publisherName)
    
    def getPublishYearNode(self, publishYear) :
        return DataQuery._getNode(PublishYear, publishYear)

    def getBookNodeAndRelationships(self, book_title) :
        book = self.getBookNode(book_title)
        if (book):
            authorNames = []
            authors= book.authors
            for author in authors :
                authorNames.append(author.name)
            
            categories = []
            relatedCategories = book.categories
            for relatedCategory in relatedCategories :
                categories.append(relatedCategory.name)
            
            publisher = book.publisher[0].name
            publishedYear = book.publishYear[0].name
            
            return book, authorNames, categories, publisher, publishedYear
        else :
            return None
            

##################TEST use
data_query = DataQuery()
author = data_query.getAuthorNode(authorName="Everett Ferguson")
if author:
    print(author)
else :
    print('not exist')
    
book = data_query.getBookNode(book_title="Beginner's Yoruba (Hippocrene Beginner's Series)")
if book:
    print(book)
else :
    print('not exist')
    
    
'''
https://neomodel.readthedocs.io/en/latest/queries.html

lt - less than
gt - greater than
lte - less than or equal to
gte - greater than or equal to
ne - not equal
in - item in list
isnull - True IS NULL, False IS NOT NULL
exact - string equals
iexact - string equals, case insensitive
contains - contains string value
icontains - contains string value, case insensitive
startswith - starts with string value
istartswith - starts with string value, case insensitive
endswith - ends with string value
iendswith - ends with string value, case insensitive
regex - matches a regex expression
iregex - matches a regex expression, case insensitive

e.g.
Lang.nodes.filter(
    Q(name__startswith='Py'),
    Q(year=2005) | Q(year=2006)
)
'''