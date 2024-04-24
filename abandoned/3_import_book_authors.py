from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, UniqueIdProperty, DateProperty, ArrayProperty, FloatProperty

#bookId,Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount

class Author(StructuredNode) :
    name = StringProperty(UniqueIdProperty=True, required=True)

class Book(StructuredNode):
    Title = StringProperty(unique_index=True, required=True)  # 标题作为唯一标识
    description = StringProperty()
    image = StringProperty()
    previewLink = StringProperty()
    # publisher = StringProperty()
    infoLink = StringProperty()
    # categories = ArrayProperty(StringProperty())  # 分类可能有多个
    ratingsCount = FloatProperty()
    authors = RelationshipTo(Author, 'AUTHORED_BY')

import csv
def importBooks(csvFile):
    with open(csvFile, 'r', encoding='utf-8') as file :
        reader = csv.DictReader(file)
        index=0
        for row in reader :
            book = Book(
                Title=row['Title'],
                description=row['description'],
                image=row['image'],
                previewLink=row['previewLink'],
                # publisher=row['publisher'],
                infoLink=row['infoLink'],
                # categories=row['categories'].strip("[]").replace("'", "").split(", "),
                ratingsCount=float(row['ratingsCount'])
            )
            book.save()
            index+=1
            print(f'index={index}')
            authors = row['authors'].strip("[]").replace("'", "").split(", ")
            for authorName in authors:
                author_list = Author.get_or_create({'name': authorName})
                author = author_list[0] if author_list else None
                if author:
                    book.authors.connect(author)

importBooks('./archive/split_data_title_information.csv')
