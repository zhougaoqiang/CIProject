from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, UniqueIdProperty, DateProperty, ArrayProperty, FloatProperty

class Book(StructuredNode) :
    Title = StringProperty(unique_index=True, required=True)
    publisher = RelationshipTo('Publisher', 'PUBLISHED_BY')
    
class Publisher(StructuredNode) :
    name = StringProperty(unique_index=True, required=True)
    
import csv
import ast

def importBookPublisher(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader :
            book_title = row['Title']
            publisherName = row['publisher']
            
            book = Book.nodes.get(Title=book_title) ##confirm have 
            if publisherName :
                publisher = Publisher.get_or_create({'name': publisherName})[0]
                if not book.publisher.is_connected(publisher) :
                    book.publisher.connect(publisher)
                    print(f"connected {book.Title} to publisher {publisher.name}")
                        
importBookPublisher('./archive/split_data_title_publisher.csv')