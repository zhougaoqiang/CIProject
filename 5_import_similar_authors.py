from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, UniqueIdProperty, DateProperty, ArrayProperty, FloatProperty

class Author(StructuredNode) :
    name = StringProperty(unique_index=True, required=True)
    similar_to = RelationshipTo('Author', 'SIMILAR_TO')

import csv
import ast

def importSimilarAuthors(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        authors={}
        
        for row in reader :
            authorName=row['name']
            authors[authorName] = Author.get_or_create({"name":authorName})[0]
            
        file.seek(0)
        next(reader) ##no need for header
        for row in reader :
            author = authors[row['name']]
            similarNames=ast.literal_eval(row['similar_names'])
            for name in similarNames :
                if name:
                    name_list = [n.strip() for n in name.split(',') if n.strip()]
                    for sim_name in name_list :
                        if sim_name in authors :
                            similarAuthor = authors[sim_name]
                            if not author.similar_to.is_connected(similarAuthor) :
                                author.similar_to.connect(similarAuthor)
                                print(f"Connect {author.name} to {similarAuthor.name} as similar")

importSimilarAuthors('./archive/author_similar.csv')                    