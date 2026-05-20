
from django.utils.cache import add_never_cache_headers

class NoCacheMiddleware:
    """
    Middleware that adds 'Cache-Control: no-cache, no-store, must-revalidate' 
    headers to all responses for authenticated users to prevent back-button 
    access to sensitive pages after logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only apply to authenticated users to secure private pages
        if hasattr(request, 'user') and request.user.is_authenticated:
            add_never_cache_headers(response)
            
        return response
