from bookDataImporter import BookDataImporter
import sys
args = sys.argv
options = args[1:]

def analyseParameter(options) :
    clearDatabase=False
    for option in options :
        if option == '-c' :
            print("NOTE: YOU ARE CHOOSE TO INIT DATABASE AND IMPORT DATA")
            clearDatabase=True
            break
    return clearDatabase

filename = "./archive/books01.csv"
importer = BookDataImporter(filename, 65)
clearDatabase = analyseParameter(options=options)
importer.importBookFromServer(clearDatabase)
