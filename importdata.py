import pandas as pd
import dataprocessfunctions
import sys
args = sys.argv
options = args[1:]

readFromRawData, sampleSize = dataprocessfunctions.analyseParameter(options)
    
input_file = "./archive/books_raw_data.csv"
actual_read_file = "./archive/books_data.csv"

if readFromRawData :
    dataprocessfunctions.read_save_csv(input_file, actual_read_file)

if sampleSize != 0 :
    actual_read_file = dataprocessfunctions.split_csv_pandas(actual_read_file, "./archive/books_data", sampleSize)
    
authorFile, categoryFile, publisherFile, publishYearFile, ratingFile = dataprocessfunctions.split_files_to_review(actual_read_file, "./archive/split_data")

#####step 1: import book labels and name labels.
dataprocessfunctions.importBooks(actual_read_file)

#####step 2: import similar name relationship
dataprocessfunctions.extractAuthors(authorFile, similarityThreshold=75)
dataprocessfunctions.connectSimilarAuthors(authorFile)

#####step 3: import categories
dataprocessfunctions.importAndConnectBookCategories(categoryFile)

#####step 4: import publisher
dataprocessfunctions.importAndConnectBookPublisher(publisherFile)