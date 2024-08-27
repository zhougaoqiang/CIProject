from django.http import JsonResponse
from django.views import View
from .dataqueryservice import DataQuery
import json
import pandas as pd
from .bookDataImporter import BookDataImporter

class BookAPI(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_query = DataQuery()

    def get(self, request):
        action = request.GET.get('action', '')
        if action == 'get-by-name':
            return self.get_book_by_name(request)
        elif action == 'get-by-contain-name':
            return self.search_book_by_contain_name(request)
        elif action == 'fuzzy-search-book' :
            return self.fuzzy_seach_book(request)
        elif action == 'get-book-by-author': #####updated
            return self.get_book_by_author(request)
        elif action == 'get-all-books' :
            return self.get_all_books(request)
        elif action == 'get-books-counts' :
            return self.get_books_counts(request)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        """_summary_
    {
    "add-books":
        [{
            "title": "Bruce Lee: The Incomparable Fighter",
            "authors": [ "M. Uyehara"]
        },
        {
            "title": "The Bruce Lee Story",
            "authors": ["Mike Lee","Linda Lee"]
        }]
    }
        """
        
    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action', '')

            if action == 'add-books':
                return self.add_books_to_database(data) #####error code: 0-no error, 1-has exist book.
            elif action == 'delete-book' :
                return self.delete_book(data) #####error code: 0-no error, 1-no find book, 2-delete fail
            elif action == 'update-book':
                return self.update_book(data)
            else:
                return JsonResponse({'error': 'Invalid request'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    def get_book_by_name(self, request):
        book_name = request.GET.get('name')
        if book_name:
            data = self.data_query.getBookWithRelationships(book_title=book_name)
            if data:
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find book'}, status=404)
        else:
            return JsonResponse({'error': 'No book name provided'}, status=400)

    def search_book_by_contain_name(self, request):
        book_name = request.GET.get('name')
        ignore_case = request.GET.get('ignorecase', 'True').lower() == 'true'
        if book_name:
            data = self.data_query.searchBooksByContains(bookTitle=book_name, ignorecase=ignore_case)
            if data:
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any book'}, status=404)
        else:
            return JsonResponse({'error': 'No book name provided'}, status=400)
    
    def fuzzy_seach_book(self, request):
        author_name = request.GET.get('author', '')
        book_title = request.GET.get('book', '')
        print(author_name)
        print(book_title)
        data = self.data_query.fuzzySearchBooks(author=author_name, title=book_title)
        if data:
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'error': 'Cannot find any book'}, status=404)
        
    def get_book_by_author(self, request) :
        author_name = request.GET.get('author-name')
        if author_name :
            data = self.data_query.getBookByAuthor(author_name)
            if data:
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any book'}, status=404)
        return JsonResponse({'error': 'No book name provided'}, status=400)
    
    def get_all_books(self, request) :
        page = int(request.GET.get('page', '0'))
        limit = int(request.GET.get('limit', '10'))
        print(f'receive info order by: page:{page}, limit:{limit}')
        data = self.data_query.getBooks(page, limit)
        if data:
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'error': 'Cannot find any book'}, status=404)
        
    def get_books_counts(self, request) :
        return JsonResponse({'count' : self.data_query.getBooksCount()}, safe=False)

    def add_books_to_database(self, data) :
        df = self.__json_to_dataframe(json_data=data)
        importer = BookDataImporter('', 65)
        existedBooks = importer.importBookFromWeb(df)
        if len(existedBooks) == 0:
            return JsonResponse({"error": 0}, safe=False)
        else :
            return JsonResponse(self.__to_json(existedBooks), safe=False)

    def delete_book(self, data) :
        booktitle = data.get('book-title', '')
        rtn = self.data_query.deleteBookNode(booktitle)
        return JsonResponse({"error": rtn}, safe=False)
    
    def update_book(self, data) :
        bookTitle = data.get('book-title', '')
        authors = data.get('authors', [])
        rtn = self.data_query.deleteBookNode(bookTitle)
        if rtn == 2:
            return JsonResponse({"error": 1}, safe=False)
        
        info = []
        info.append({{'Title': bookTitle, 'authors': authors}})
        df = pd.DataFrame(info, columns=['Title', 'authors'])
        importer = BookDataImporter('', 65)
        importer.importBookFromWeb(df)
        return JsonResponse({"error": 0}, safe=False)
    

    def __to_json(list):
        books_list = []
        for row in list:
            books_list.append({
                "title" : row[0],
                "authors" : row[1]
            })
        json_result = {"error" : 1, "exist-books": books_list}
        return json_result        

    def __json_to_dataframe(self, json_data) :
        books = json_data.get('add-books', [])
        data = []
        for book in books:
            title = book.get('title')
            authors = ', '.join(book.get('authors', []))  # Join multiple authors with a comma
            data.append({'Title': title, 'authors': authors})
        df = pd.DataFrame(data, columns=['Title', 'authors'])
        return df

###########################################################################################################################
###########################################################################################################################
class AuthorAPI(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_query = DataQuery()

    def get(self, request):
        action = request.GET.get('action', '')
        print(f'action = {action}')
        if action == 'get-authors-count' :
            return self.get_authors_counts(request)
        elif action == 'get-author-info' :
            return self.get_author_info(request)
        elif action == 'get-by-contain-name' :
            return self.get_contain_name(request)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
    def get_authors_counts(self, request) :
        return JsonResponse({'count' : self.data_query.getAuthorsCount()}, safe=False)
    
    def get_author_info(self, request):
        name = request.GET.get('name', '')
        if name:
            data = self.data_query.getAuthorInfo(name)
            if data:
                return JsonResponse({'author': data}, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find author'}, status=404)
        else:
            return JsonResponse({'error': 'No author name provided'}, status=400)
    
    def get_similar_authors(self, request) :
        name = request.GET.get('name', '')
        threshold = int(request.GET.get('threshold', '75'))
        if name:
            data = self.data_query.findSimilarAuthors(name, threshold)
            if data:
                similar_name_info =[]
                for name in data:
                    similar_name_info.append(self.data_query.getAuthorInfo(name))
                return JsonResponse({'authors': similar_name_info}, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find author'}, status=404)
        else:
            return JsonResponse({'error': 'No author name provided'}, status=400)
        
    def get_contain_name(self, request) :
        name = request.GET.get('name', '')
        ignore_case = request.GET.get('ignorecase', 'True').lower() == 'true'
        if name:
            data = self.data_query.searchAuthorsByContains(name,ignore_case)
            if data:
                return JsonResponse({'authors': data}, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any author'}, status=404)
        else:
            return JsonResponse({'error': 'No author name provided'}, status=400)