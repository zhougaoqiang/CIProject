from neomodel import config
config.DATABASE_URL = 'bolt://neo4j:OKOKOKOK@localhost:7687'

from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, UniqueIdProperty, DateProperty, ArrayProperty, FloatProperty

class Author(StructuredNode) :
    name = StringProperty(unique_index=True, required=True)
    similar_to = RelationshipTo('Author', 'SIMILAR_TO')

import Levenshtein
import csv

def checkSimilarity(str1, str2) :
    len1 = len(str1)
    len2 = len(str2)
    maxLen = len1
    if (maxLen < len2):
        maxLen = len2
    similarity = (1 - Levenshtein.distance(str1, str2)/maxLen) * 100
    return similarity

def sortName(name) :
    name = name.lower()
    words = name.split()
    sorted_words = sorted(words)
    return " ".join(sorted_words)

def importAutorsAndSimilarities(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader :
            author, created = Author.get_or_create({'name': row['author_name']})