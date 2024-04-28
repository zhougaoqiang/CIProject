from django.http import JsonResponse
from django.views import View
from .dataqueryservice import DataQuery

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
        elif action == 'get-book-by-start-with':
            return self.search_book_by_start_with(request)
        elif action == 'fuzzy-search-book' :
            return self.fuzzy_seach_book(request)
        elif action == 'find-similar-books':
            return self.find_similar_books(request)
        elif action == 'get-book-by-link':
            return self.get_book_by_link(request)
        elif action == 'get-all-books' :
            return self.get_all_books(request)
        elif action == 'get-books-counts' :
            return self.get_books_counts(request)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

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
        ignore_case = request.GET.get('ignorecase', 'False').lower() == 'true'
        if book_name:
            data = self.data_query.searchBooksByContains(bookTitle=book_name, ignorecase=ignore_case)
            if data:
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any book'}, status=404)
        else:
            return JsonResponse({'error': 'No book name provided'}, status=400)
        
    def search_book_by_start_with(self, request):
        book_name = request.GET.get('name')
        ignore_case = request.GET.get('ignorecase', 'False').lower() == 'true'
        if book_name:
            data = self.data_query.searchBooksByStartWith(bookTitle=book_name, ignorecase=ignore_case)
            if data:
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any book'}, status=404)
        else:
            return JsonResponse({'error': 'No book name provided'}, status=400)
    
    def fuzzy_seach_book(self, request):
        author_name = request.GET.get('author', '')
        category_name = request.GET.get('category', '')
        publisher_name = request.GET.get('publisher', '')
        startyear = int(request.GET.get('startpublishedyear', '0'))
        endyear = int(request.GET.get('endpublishedyear', '0'))
        if endyear > startyear :
            endyear = startyear
        print(author_name)
        print(category_name)
        print(publisher_name)
        print(startyear)
        print(endyear)
        data = self.data_query.fuzzySearchBooks(author=author_name, 
                                                category=category_name, 
                                                publisher=publisher_name, 
                                                startPublishedYear=startyear,
                                                endPublishedYear=endyear)
        if data:
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'error': 'Cannot find any book'}, status=404)
        
    def find_similar_books(self,request) :
        book_name = request.GET.get('name')
        threshold = int(request.GET.get('threshold', '75'))
        print(f'receive info {book_name}, {threshold}')
        if book_name:
            data = self.data_query.findSimilarBooks(book_name=book_name, threshold=threshold)
            if data:
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any book'}, status=404)
        else:
            return JsonResponse({'error': 'No book name provided'}, status=400)
        
    def get_book_by_link(self, request) :
        link_type = request.GET.get('link')
        if link_type == 'category' :
            category_name = request.GET.get('category-name')
            if category_name :
                data = self.data_query.getCategoryWithRelationships(category_name)
                if data:
                    return JsonResponse(data, safe=False)
                else:
                    return JsonResponse({'error': 'Cannot find any book'}, status=404)
        elif link_type == 'author' :
            author_name = request.GET.get('author-name')
            if author_name :
                data = self.data_query.getBookByAuthor(author_name)
                if data:
                    return JsonResponse(data, safe=False)
                else:
                    return JsonResponse({'error': 'Cannot find any book'}, status=404)
        elif link_type == 'publisher' :
            publisher_name = request.GET.get('publisher-name')
            if publisher_name :
                data = self.data_query.getPublisherWithRelationships(publisher_name)
                if data:
                    return JsonResponse(data, safe=False)
                else:
                    return JsonResponse({'error': 'Cannot find any book'}, status=404)
        elif link_type == 'publishedyear' :
            start_year = int(request.GET.get('start-year', '0'))
            end_year = int(request.GET.get('end-year', '0'))
            book_list = []
            if start_year < end_year : ##sort from 1986 to 1987 
                while start_year <= end_year :
                    book_list.append(self.data_query.getPublishYearWithRelationships(start_year))
                    start_year +=1
            elif end_year < start_year : ##sort from 1987 to 1986 descend
                while start_year >= end_year :
                    book_list.append(self.data_query.getPublishYearWithRelationships(start_year))
                    start_year -=1
            else :
                book_list.append(self.data_query.getPublishYearWithRelationships(start_year))
            data = {'books': book_list}
            print(f'start: {start_year}, end:{end_year}')
            return JsonResponse(data, safe=False)

        return JsonResponse({'error': 'No book name provided'}, status=400)
    
    def get_all_books(self, request) :
        orderby = request.GET.get('order-by', '') ##support 'title', 'ratingsCount', 'publishDate'
        isDesc = request.GET.get('isDesc', 'False').lower() == 'true'
        page = int(request.GET.get('page', '0'))
        limit = int(request.GET.get('limit', '10'))
        print(f'receive info order by:{orderby}, isDesc:{isDesc}, page:{page}, limit:{limit}')
        data = self.data_query.getBooks(orderby, isDesc, page, limit)
        if data:
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'error': 'Cannot find any book'}, status=404)
        
    def get_books_counts(self, request) :
        return JsonResponse({'count' : self.data_query.getBooksCount()}, safe=False)


class OtherAPI(View):
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
        elif action == 'get-similar-authors' :
            return self.get_similar_authors(request)
        elif action == 'get-by-contain-name' :
            return self.get_contain_name(request)
        elif action == 'get-by-start-with-name':
            return self.get_start_with_name(request)
        elif action == 'get-all-categories' :
            return self.get_all_categories(request)
        elif action == 'get-all-published-year':
            return self.get_all_published_year(request)
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
        ignore_case = request.GET.get('ignorecase', 'False').lower() == 'true'
        if name:
            data = self.data_query.searchAuthorsByContains(name,ignore_case)
            if data:
                return JsonResponse({'authors': data}, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any author'}, status=404)
        else:
            return JsonResponse({'error': 'No author name provided'}, status=400)
        
    def get_start_with_name(self, request):
        name = request.GET.get('name', '')
        ignore_case = request.GET.get('ignorecase', 'False').lower() == 'true'
        if name:
            data = self.data_query.searchAuthorByStartWith(name,ignore_case)
            if data:
                return JsonResponse({'authors': data}, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any author'}, status=404)
        else:
            return JsonResponse({'error': 'No author name provided'}, status=400)
        
    def get_all_categories(self, request) :
        return JsonResponse({'categories': self.data_query.getAllCategories()}, safe=False)
    
    def get_all_published_year(self, request) :
        return JsonResponse({'pulishedyear': self.data_query.getAllPulishedYear()}, safe=False)