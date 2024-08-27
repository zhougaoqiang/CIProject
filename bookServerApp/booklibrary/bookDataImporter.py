import pandas as pd
import Levenshtein
from itertools import combinations
from .bookModels import Book, Author
from neomodel import db

#######################################################################################################################################################################
#############################################################################V2 FUNCTIONS##############################################################################
#######################################################################################################################################################################

class BookDataImporter :
    def __init__(self, filaname, similarityThreshold):
        self.filename = filaname
        self.similarityThreshold = similarityThreshold
    
    #############public functions#############
    def importBookFromServer(self, needClearDatabase) :
        #step 1: init database
        if needClearDatabase :
            self.__clearDatabase()
        #step 2: create nodes
        existedBooks, newAuthorNodes, existAuthorNodes = self.__importBook()
        for book in existedBooks :
            print(f"book({book[0]} is already exist)")
        #step3: create relationships
        self.__createRelationshipAmongAuthors(newAuthorNodes, existAuthorNodes)
        
    def importBookFromWeb(self, df) :
        existBooks, newAuthorNodes, existAuthorNodes = self.__importBookAndAuthorFromDataFrame(df, True)
        self.__createRelationshipAmongAuthors(newAuthorNodes, existAuthorNodes)
        return existBooks
    
    #############private functions#############
    def __importBook(self) :
        df = self.__readCSV()
        updateDf, removedDf = self.__splitNullData(df)
        existBooks, newAuthorNodes, existAuthorNodes = self.__importBookAndAuthorFromDataFrame(updateDf, False)
        return existBooks, newAuthorNodes, existAuthorNodes
    
    def __splitNullData(self, inputDataFrame):
        any_missing=inputDataFrame.isnull().any(axis=1)
        updatedDF = inputDataFrame[~any_missing]
        removedDF = inputDataFrame[any_missing]
        return updatedDF, removedDF

    def __readCSV(self):
        df = pd.read_csv(self.filename)
        return df

    #this function is uesed to avoid fifferent writing habits
    def __sortName(self, name) :
        name = name.lower()
        words = name.split()
        sorted_words = sorted(words)
        return " ".join(sorted_words)

    def __checkSimilarity(self, str1, str2):
        maxLen = max(len(str1), len(str2))
        similarity = (1 - Levenshtein.distance(str1, str2) / maxLen) * 100
        return similarity

    def __clearDatabase(self):
        db.cypher_query("MATCH (n) DETACH DELETE n")

    def __importBookAndAuthorFromDataFrame(self, df, isWeb) :
        existedBook = []
        newAuthorNodes = []
        oldAuthorNodes = []
        for index, row in df.iterrows():
            try:
                books = Book.nodes.filter(title=row['Title'])
                if books :
                    existedBook.append([row['Title'], row['authors']])
                    continue
                book = Book(title=row['Title'])
                book.save()
                
                # directly create and connect author nodes
                if isWeb:
                    authors = row['authors']
                else :
                    authors = eval(row['authors'])

                for author in authors:
                    print(f"author={author}")
                    authorNodes = Author.nodes.filter(name=author)
                    if authorNodes:
                        authorNode = Author.nodes.get(name=author)
                        book.authors.connect(authorNode)
                        oldAuthorNodes.append(authorNode)
                    else:
                        authorNode = Author.get_or_create({'name': author, 'orderedName': self.__sortName(author)})[0]
                        if authorNode:
                            book.authors.connect(authorNode)
                            newAuthorNodes.append(authorNode)
            except Exception as e:
                print(f"Process index={index} (Title: {row['Title']}) import failed: {e}")
        return existedBook, newAuthorNodes, oldAuthorNodes

    def __createRelationshipBetweenNewAuthors(self, newAuthorNodes):
        for a,b in combinations(newAuthorNodes,2) :
            similarity = self.__checkSimilarity(a.orderedName, b.orderedName)
            if similarity > self.similarityThreshold :
                print(f"Author({a.name}) and author({b.name} has similar name)")
                a.similar_with.connect(b)    

    def __createRelationshipWithExistingAuthors(self, newAuthorNodes, existAuthorNodes) :
        if len(existAuthorNodes) == 0 :
            print("no existing author")
            return
        if  len(newAuthorNodes) == 0 :
            print("no new author")
            return
        
        for newAuthorNode in newAuthorNodes :
            for node in existAuthorNodes :
                if node.name == newAuthorNode.name : #do not compare self
                    continue
                similarity = self.__checkSimilarity(node.orderedName, newAuthorNode.orderedName)
                if similarity > self.similarityThreshold :
                    print(f"New Author({newAuthorNode.name}) and exist author({node.name} has similar name)")
                    node.similar_with.connect(newAuthorNode)

    def __createRelationshipAmongAuthors(self, newAuthorNodes, existAuthorNodes) :
        self.__createRelationshipWithExistingAuthors(newAuthorNodes, existAuthorNodes)
        self.__createRelationshipBetweenNewAuthors(newAuthorNodes)