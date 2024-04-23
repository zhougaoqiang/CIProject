from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, UniqueIdProperty, DateProperty, ArrayProperty, FloatProperty

class Book(StructuredNode) :
    Title = StringProperty(unique_index=True, required=True)
    categories = RelationshipTo('Category', 'HAS_CATEGORY')
    
class Category(StructuredNode) :
    name = StringProperty(unique_index=True, required=True)
    
import csv
import ast

def importBookCategories(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader :
            book_title = row['Title']
            categories = ast.literal_eval(row['categories'])
            
            book = Book.nodes.get(Title=book_title) ##confirm have 
            
            for category_name in categories :
                if category_name :
                    category= Category.get_or_create({'name':category_name})[0]
                    if not book.categories.is_connected(category) :
                        book.categories.connect(category)
                        print(f"connected {book.Title} to category {category.name}")
                        
importBookCategories('./archive/split_data_title_categories.csv')