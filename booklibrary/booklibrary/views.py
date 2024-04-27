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
        print(book_name)
        print(ignore_case)
        if book_name:
            data = self.data_query.searchBooksByContains(bookTitle=book_name, ignorecase=ignore_case)
            if data:
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Cannot find any book'}, status=404)
        else:
            return JsonResponse({'error': 'No book name provided'}, status=400)
