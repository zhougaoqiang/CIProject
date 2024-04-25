from models import Book, Author, Category, Publisher, PublishYear
import json
import Levenshtein

class DataQuery :
    def __init__(self) :
        print("Create DataQuery")
    
######################################################################
###################### generic fetch node functions #################
###################### directky return json format ##################    
######################################################################

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

    def getBookWithRelationships(self, book_title):
        book = self.getBookNode(book_title)
        if book:
            author_names = [{"name": author.name, "link": f"/authors/{author.name}"} for author in book.authors]
            categories = [{"name": related_category.name, "link": f"/categories/{related_category.name}"} for related_category in book.categories]
            publisher_link = f"/publishers/{book.publisher[0].name}" if book.publisher else None
            published_year_link = f"/years/{book.publishYear[0].name}" if book.publishYear else None
        
            # Create a dictionary with book details and relationships
            book_data = {
                "title": book.title,
                "description": book.description,
                "image": book.image,
                "previewLink": book.previewLink,
                "infoLink": book.infoLink,
                "ratingsCount": book.ratingsCount,
                "authors": author_names,
                "categories": categories,
                "publisher": {"name": book.publisher[0].name, "link": publisher_link} if publisher_link else None,
                "publishedYear": {"name": book.publishYear[0].name, "link": published_year_link} if published_year_link else None
            }
        
            # Convert the dictionary to JSON format
            book_json = json.dumps(book_data)
            return book_json
        else:
            return None
            
    def getAuthorWithRelationships(self, authorName) :
        author = self.getAuthorNode(authorName=authorName)
        if author :
            writebooks = [{"book": book.title, "link": f"/authors/{book.title}"} for book in author.books]
            similar_names = [{"name": author.name, "link": f"/authors/{author.name}"} for author in author.similar_with]

            author_data = {
                "name" : author.name,
                "books" : writebooks,
                "similar_names" : similar_names
            }
            return json.dumps(author_data)
        else :
            return None
        
    def getCategoryWithRelationships(self, category_Name) :
        category = self.getCategoryNode(categoryName=category_Name)
        if category :
            books = [{"book": book.title, "link": f"/authors/{book.title}"} for book in category.books]
            category_data = {
                "name" : category.name,
                "books" : books
            }
            return json.dumps(category_data)
        else :
            return None
    
    def getPublisherWithRelationships(self, publisher_Name) :
        publisher = self.getPublisherNode(publisherName=publisher_Name)
        if publisher :
            books = [{"book": book.title, "link": f"/authors/{book.title}"} for book in publisher.books]
            publisher_data = {
                "name" : publisher.name,
                "books" : books
            }
            return json.dumps(publisher_data)
        else :
            return None
        
    def getPublishYearWithRelationships(self, published_Year) :
        published = self.getPublishYearNode(publishYear=published_Year)
        if published :
            books = [{"book": book.title, "link": f"/authors/{book.title}"} for book in published.books]
            publisher_data = {
                "name" : published.name,
                "books" : books
            }
            return json.dumps(publisher_data)
        else :
            return None


######################################################################
###################### author related functions #####################
######################################################################

    def getAuthors(self, orderBy, page, limit) :
        try :
            if page > 0 :
                return Author.nodes.order_by(orderBy).skip(limit*page).limit(limit)
            else :
                return Author.nodes.order_by(orderBy).limit(limit)
        except Exception as e:
            print(f'get authors function execute file [{orderBy}, {page}, {limit}]')
            return None
        
    def getAuthorsCount(self) :
        return Author.nodes.count()
    
    def searchAuthorsByContains(self, authorname, ignorecase=False):
        if ignorecase :
            return Author.nodes.filter(name__icontains=authorname)
        else :
            return Author.nodes.filter(name__contains=authorname)

    def searchAuthorByStartWith(self, authorname, ignorecase=False) :
        if ignorecase :
            return Author.nodes.filter(name__istartswith=authorname)
        else :
            return Author.nodes.filter(name__startswith=authorname)

    def searchAuthorByRegex(self, authorname, ignorecase=False) :
        if ignorecase :
            return Author.nodes.filter(name__iregex=authorname)
        else :
            return Author.nodes.filter(name__regex=authorname)
    
    @staticmethod
    def sortName(name) :
        name = name.lower()
        words = name.split()
        sorted_words = sorted(words)
        return " ".join(sorted_words)

    @staticmethod
    def checkSimilarity(sorted_str1, str2) :
        len1 = len(sorted_str1)
        len2 = len(str2)
        maxLen = len1
        if (maxLen < len2):
            maxLen = len2
        similarity = (1 - Levenshtein.distance(sorted_str1, DataQuery.sortName(str2)/maxLen)) * 100
        return similarity

    def findSimilarAuthors(self, author_name, threshould) :
        authors = Author.nodes.all()
        authorNames = [author.name for author in authors]
        similar_names = []
        author_name = DataQuery.sortName(author_name)
        for authorname in authorNames :
            similar_threshold = DataQuery.checkSimilarity(author_name, authorname)
            if similar_threshold > threshould :
                similar_names.append([authorname, similar_threshold])
        ##sorted by similar_threshold, and descending order
        similar_names_sorted = sorted(similar_names, key=lambda x: x[1], reverse=True)
        return similar_names_sorted


        


##################TEST use
data_query = DataQuery()

##Test1
'''
author = data_query.getAuthorNode(authorName="Everett Ferguson")
if author:
    print(author)
else :
    print('not exist')
'''

###Test2
'''
book = data_query.getBookNode(book_title="Beginner's Yoruba (Hippocrene Beginner's Series)")
if book:
    print(book)
else :
    print('not exist')
'''

###Test3
'''
authorInfos = data_query.getBookWithRelationships(book_title="Beginner's Yoruba (Hippocrene Beginner's Series)")
print(authorInfos)
'''

###Test4
'''
info = data_query.getAuthorWithRelationships(authorName="Richard Overy")
print(info)
'''

###Test5
'''
info = data_query.getCategoryWithRelationships(category_Name="Performing Arts")
print(info)
'''

###test6
'''
info = data_query.getPublisherWithRelationships(publisher_Name="Univ of California Press")
print(info)
'''

###test7
'''
info = data_query.getPublishYearWithRelationships(published_Year=2010)
print(info)
'''


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