import pandas as pd
import os
import csv
import Levenshtein
import ast
from models import Book, Author, Category, Publisher, PublishYear

def analyseParameter(options) :
    readFromRawData = False
    sampleSize = 0
    for option in options :
        if option == '-r' :
            print("receive -r: read from raw data again")
            readFromRawData=True
        elif option.startswith('-s'):
            try:
                sampleSize = int(option[2:])
            except ValueError:
                print(f"Invalid sample size: {option}")
    return readFromRawData, sampleSize

def clean_cell_quotes(df):
    df['authors'] = df['authors'].apply(lambda x: x.replace("'", "\'"))
    return df

def read_save_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    any_missing = df.isnull().any(axis=1)
    df = df.drop(any_missing[any_missing].index)
    # df = clean_cell_quotes(df)
    df.to_csv(output_file, index=False)

def split_csv_pandas(input_file, output_prefix, chunksize=10000):
    reader = pd.read_csv(input_file, iterator=True, chunksize=chunksize)
    file_counter = 0
    for chunk in reader:
        output_file = f"{output_prefix}_{file_counter}.csv"

        while os.path.exists(output_file):
            file_counter += 1
            output_file = f"{output_prefix}_{file_counter}.csv"
        chunk.to_csv(output_file, index=False)
        break
    return output_file

def split_files_to_review(input_file, output_prefix) :
    df = pd.read_csv(input_file)
    authorFile_cols = ['Title', 'authors']
    categoryFile_cols = ['Title', 'categories']
    publisherFile_cols = ['Title', 'publisher']
    publishYearFile_cols = ['Title', 'publishedDate']
    # ratingFile_cols = ['Title', 'ratingsCount']
    
    authorFile_df = df[authorFile_cols]
    categoryFile_df = df[categoryFile_cols]
    publisherFile_df = df[publisherFile_cols]
    publishYearFile_df = df[publishYearFile_cols]
    # ratingFile_df = df[ratingFile_cols]
    
    authorFile = f"{output_prefix}_authors.csv"
    categoryFile = f"{output_prefix}_categories.csv"
    publisherFile = f"{output_prefix}_publishers.csv"
    publishYearFile = f"{output_prefix}_publishyears.csv"
    # ratingFile = f"{output_prefix}_ratings.csv"
    
    authorFile_df.to_csv(authorFile, index=False)
    categoryFile_df.to_csv(categoryFile, index=False)
    publisherFile_df.to_csv(publisherFile, index=False)
    publishYearFile_df.to_csv(publishYearFile, index=False)
    # ratingFile_df.to_csv(ratingFile, index=False)
    return authorFile, categoryFile, publisherFile, publishYearFile

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
 
def extractAuthors(inputFile, similarityThreshold=80):
    nameSet = set()
    with open(inputFile, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            authors_list = eval(row['authors'])
            for author in authors_list:
                nameSet.add(author)

    nameList = [['name', 'sorted_name', 'similar_names']]
    sorted_names = {name: sortName(name) for name in nameSet} ##dict

    for name, sorted_name in sorted_names.items() :
        similar_names = []
        for other_name in nameSet:
            if name != other_name :
                if checkSimilarity(sorted_names[name], sorted_names[other_name]) >= similarityThreshold :
                    similar_names.append(other_name)
        nameList.append([name, sorted_name, [", ".join(similar_names)]])

    with open(inputFile, 'w', newline='', encoding='utf-8') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(nameList)
        
def importBooks(csvFile):
    with open(csvFile, 'r', encoding='utf-8') as file :
        reader = csv.DictReader(file)
        index=0
        for row in reader :
            try :
                book = Book(
                    title=row['Title'],
                    description=row['description'],
                    image=row['image'],
                    previewLink=row['previewLink'],
                    infoLink=row['infoLink'],
                    ratingsCount=float(row['ratingsCount']),
                    publishDate = row['publishedDate']
                )
                book.save()
                index+=1
                # print(f'index={index}')
                authors = eval(row['authors'])
                for authorName in authors:
                    author = Author.get_or_create({'name': authorName})[0]
                    if author:
                        book.authors.connect(author)
            except Exception as e :
                print(f"process index={index} fail : {e}")
                    
def connectSimilarAuthors(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        authors={}
        
        for row in reader :
            authorName=row['name']
            authorName = row['name']
            matching_authors = Author.nodes.filter(name=authorName)
            if len(matching_authors) == 1:
                authors[authorName] = matching_authors[0]
            elif len(matching_authors) > 1:
                print(f"Warning: Found multiple authors for name '{authorName}'")
                authors[authorName] = matching_authors[0]
            else:
                print(f"No author found for name '{authorName}'")
            
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
                            if not author.similar_with.is_connected(similarAuthor) :
                                author.similar_with.connect(similarAuthor)
                                print(f"Connect {author.name} to {similarAuthor.name} as similar")
                                
def importAndConnectBookCategories(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader :
            book_title = row['Title']
            categories = ast.literal_eval(row['categories'])
            
            book = Book.nodes.get(title=book_title) ##confirm have 
            for category_name in categories :
                if category_name :
                    category= Category.get_or_create({'name':category_name})[0]
                    if not book.categories.is_connected(category) :
                        book.categories.connect(category)
                        print(f"connected {book.title} to category {category.name}")                                

def importAndConnectBookPublisher(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader :
            book_title = row['Title']
            publisherName = row['publisher']
            
            book = Book.nodes.get(title=book_title) ##confirm have 
            if publisherName :
                publisher = Publisher.get_or_create({'name': publisherName})[0]
                if not book.publisher.is_connected(publisher) :
                    book.publisher.connect(publisher)
                    print(f"connected {book.title} to publisher {publisher.name}")

def extract_year(date_str):
    try:
        # Assuming date_str is in the format YYYY-MM-DD
        year = date_str.split('-')[0]
        return int(year)
    except Exception as e:
        # Handle any errors such as invalid date format
        print(f"Error extracting year from {date_str}: {e}")
        return int(0)


def importAndConnectBookPublishDate(csv_file) :
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader :
            book_title = row['Title']
            publishedDate = row['publishedDate']
            publishedYear = extract_year(publishedDate)

            book = Book.nodes.get(title=book_title) ##confirm have
            pubYear = PublishYear.get_or_create({'name': publishedYear})[0]
            if not book.publishYear.is_connected(pubYear) :
                book.publishYear.connect(pubYear)
                print(f"connected {book.title} to publish Year {pubYear.name}")








