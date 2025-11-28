import os
from django.http import HttpResponseForbidden


class ApiKeyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = os.getenv('INTERNAL_API_KEY')
        prefixes = os.getenv('INTERNAL_API_PATH_PREFIX', '/internal-api/')
        self.prefixes = [p.strip() for p in prefixes.split(',') if p.strip()]

    def __call__(self, request):
        if self.prefixes and any(request.path.startswith(p) for p in self.prefixes):
            if not self.api_key:
                return HttpResponseForbidden('Server misconfiguration: INTERNAL_API_KEY not set')
            key = request.headers.get('X-API-KEY') or request.META.get('HTTP_X_API_KEY')
            if not key or key != self.api_key:
                return HttpResponseForbidden('Missing or invalid API key')
        return self.get_response(request)