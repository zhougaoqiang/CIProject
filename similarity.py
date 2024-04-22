import Levenshtein

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

# str1 = "zhou Gaoqiang"
# str2 = "gaoqiang zhou"

# print(checkSimilarity(sortName(str1), sortName(str2)))

import csv
def extractAuthors(inputFile, outputFile):
    nameSet = set()
    with open(inputFile, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            authors_list = eval(row['authors'])
            for author in authors_list :
                nameSet.add(author)
                
    nameList = [['name', 'sorted_name']]
    for name in nameSet :
        sortedName = sortName(name)
        nameList.append([name, sortedName])
        
    with open(outputFile, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(nameList)
    
extractAuthors('./archive/split_data_title_authors.csv', './archive/author_similar.csv')


