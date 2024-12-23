from .models import Book, Author, Category, Publisher, PublishYear
import json
import Levenshtein
from neomodel import Q
from neomodel import db

class DataQuery :
    def __init__(self) :
        print("Create DataQuery")
    
######################################################################
###################### generic fetch node functions #################
######################################################################

    def getBookNode(self, book_title) :
        try:
            rtn = Book.nodes.get(title=book_title)
            return rtn
        except Exception as e:
            print(f'node not exist Book : {book_title}')
            return None
        
    @staticmethod
    def _getNode(nodeName, idValue) :
        try:
            rtn = nodeName.nodes.get(name=idValue)
            # print(rtn)
            return rtn
        except Exception as e:
            print(f'node not exist {nodeName}={idValue}')
            return None
    
    def getAuthorNode(self, authorName) :
        return DataQuery._getNode(Author, authorName)
    
    def getCategoryNode(self, categoryName) :
        return DataQuery._getNode(Category, categoryName)
    
    def getAllCategories(self) :
        categories = []
        for node in Category.nodes.all() :
            categories.append(node.name)
        return categories
    
    def getAllPulishedYear(self) :
        published_year = []
        years = PublishYear.nodes.order_by('name')
        for node in years :
            published_year.append(node.name)
        return published_year


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
                "publishedDate" : book.publishDate,
                "authors": author_names,
                "categories": categories,
                "publisher": {"name": book.publisher[0].name, "link": publisher_link} if publisher_link else None,
                "publishedYear": {"name": book.publishYear[0].name, "link": published_year_link} if published_year_link else None
            }

            return book_data
        else:
            return None
            
    def getAuthorWithRelationships(self, authorName) :
        author = self.getAuthorNode(authorName=authorName)
        if author :
            writebooks = [{"book": book.title, "link": f"/books/{book.title}"} for book in author.books]
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
            return {'books' : self.getBooksWithDetailByTitle([book.title for book in category.books])}
        else :
            return None
    
    def getPublisherWithRelationships(self, publisher_Name) :
        publisher = self.getPublisherNode(publisherName=publisher_Name)
        if publisher :
            return {'books' : self.getBooksWithDetailByTitle([book.title for book in publisher.books])}
        else :
            return None
        
    def getPublishYearWithRelationships(self, published_Year) :
        published = self.getPublishYearNode(publishYear=published_Year)
        if published :
            return {f'{published_Year}' : self.getBooksWithDetailByTitle([book.title for book in published.books])}
        else :
            return None
    
    def getBooksWithDetailByTitle(self, books) :
        book_list = []
        for book in books :
            book_list.append(self.getBookWithRelationships(book))
        return book_list


######################################################################
###################### author related functions #####################
######################################################################
    def getAuthorInfo(self, name) :
        author = self.getAuthorNode(name)
        if author :
            similar_authors = [sim.name for sim in author.similar_with.all()]
            books = [book.title for book in author.books.all()]
            author_info = {
                'name': author.name,
                'similar_authors': similar_authors,
                'books': books }
            return author_info
        return None

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
        return len(Author.nodes)
    
    @staticmethod
    def convertAuthorNode(authors) :
        authors_list = []
        for author in authors:
            similar_authors = [sim.name for sim in author.similar_with.all()]
            books = [book.title for book in author.books.all()]
            author_info = {
                'name': author.name,
                'similar_authors': similar_authors,
                'books': books }
            authors_list.append(author_info)
        return authors_list
    
    def searchAuthorsByContains(self, authorname, ignorecase=False):
        if ignorecase :
            return DataQuery.convertAuthorNode(Author.nodes.filter(name__icontains=authorname))
        else :
            return DataQuery.convertAuthorNode(Author.nodes.filter(name__contains=authorname))

    def searchAuthorByStartWith(self, authorname, ignorecase=False) :
        if ignorecase :
            return DataQuery.convertAuthorNode(Author.nodes.filter(name__istartswith=authorname))
        else :
            return DataQuery.convertAuthorNode(Author.nodes.filter(name__startswith=authorname))

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
        similarity = (1 - Levenshtein.distance(sorted_str1, DataQuery.sortName(str2))/maxLen) * 100
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
        author_names_only = [name[0] for name in similar_names_sorted]
        return author_names_only


######################################################################
###################### book related functions #####################
######################################################################
    @staticmethod
    def convertBookNodeToJson(books) :
        bookList=[]
        for book in books: 
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
                bookList.append(book_data)
        
        rtn = {"books" : bookList}
        return rtn

    def getBooks(self, orderBy, isDesc, page, limit):
        # Ensure the orderBy field is safe to interpolate directly into the query
        # Normally, you'd have a whitelist of allowed fields to guard against injection.
        allowed_fields = ['title', 'publishDate', 'ratingsCount']  # Example fields
        if orderBy not in allowed_fields:
            raise ValueError("Invalid order by field")

        desc = 'DESC' if isDesc else 'ASC'

        # Constructing the Cypher query string directly with order and direction
        query = f"""
            MATCH (b:Book)
            RETURN b
            ORDER BY b.{orderBy} {desc}
            SKIP $skipnumber LIMIT $limitnumber
            """

        params = {
            'skipnumber': page * limit,
            'limitnumber': limit
        }

        try:
            books, meta = db.cypher_query(query, params)
            book_list = [self.getBookWithRelationships(book[0]['title']) for book in books]
            return {'books': book_list}
        except Exception as e:
            print(f"Error executing query: {str(e)}")
        return None
    
    def getBooksCount(self) :
        return len(Book.nodes)
    
    def searchBooksByContains(self, bookTitle, ignorecase=False):
        if ignorecase :
            return DataQuery.convertBookNodeToJson(Book.nodes.filter(title__icontains=bookTitle))
        else :
            return DataQuery.convertBookNodeToJson(Book.nodes.filter(title__contains=bookTitle))
        
    def searchBooksByStartWith(self, bookTitle, ignorecase=False) :
        if ignorecase :
            return DataQuery.convertBookNodeToJson(Book.nodes.filter(title__istartswith=bookTitle))
        else :
            return DataQuery.convertBookNodeToJson(Book.nodes.filter(title__startswith=bookTitle))

    def searchBooksByRegex(self, bookTitle, ignorecase=False) :
        if ignorecase :
            return Book.nodes.filter(title__iregex=bookTitle)
        else :
            return Book.nodes.filter(title__regex=bookTitle)

    @staticmethod
    def checkBookSimilarity(str1, str2) :
        len1 = len(str1)
        len2 = len(str2)
        maxLen = len1
        if (maxLen < len2):
            maxLen = len2
        similarity = (1 - Levenshtein.distance(str1, str2)/maxLen) * 100
        return similarity
    
    def findSimilarBooks(self, book_name, threshold):
        books = Book.nodes.all()
        book_titles = [book.title for book in books]
        book_name=book_name.lower()
        similar_books = []
        for book_title in book_titles :
            similar_threshold = DataQuery.checkBookSimilarity(book_name, book_title.lower())
            if similar_threshold > threshold :
                similar_books.append([book_title, similar_threshold])
        ##sorted by similar_threshold, and descending order
        similar_names_sorted = sorted(similar_books, key=lambda x: x[1], reverse=True)
        book_list = []
        for bn in similar_names_sorted :
            book_list.append(self.getBookWithRelationships(bn[0]))
        return {'books':book_list}
    
    def fuzzySearchBooks(self, author='', category='', publisher='', startPublishedYear=0, endPublishedYear=0) :
        query = """
        MATCH (b:Book)-[:AUTHORED_BY]->(a:Author),
            (b)-[:HAS_CATEGORY]->(c:Category),
            (b)-[:PUBLISHED_BY]->(p:Publisher),
            (b)-[:PUBLISHED_YEAR]->(y:PublishYear)
        WHERE a.name CONTAINS $author_name AND
              c.name CONTAINS $category_name AND
              p.name CONTAINS $publisher_name AND
              y.name >= $startPublishedYear AND
              y.name <= $endPublishedYear
        RETURN b
        """
        params = {'author_name': author,
                  'category_name':category,
                  'publisher_name':publisher,
                  'startPublishedYear':startPublishedYear,
                  'endPublishedYear':endPublishedYear}
        books, meta = db.cypher_query(query, params)
        book_list = []
        for book in books :
            bookname = book[0]['title']
            print(f'book name is {bookname}')
            book_list.append(self.getBookWithRelationships(book[0]['title']))
        return {'books':book_list}

    def getBookByAuthor(self, author_name) :
        author = self.getAuthorNode(authorName=author_name)
        if author :
            return {'books' : self.getBooksWithDetailByTitle([book.title for book in author.books])}
        else :
            return None

##################TEST use

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