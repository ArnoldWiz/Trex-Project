import os
from django.http import HttpResponseForbidden


class ApiKeyMiddleware:
    """Middleware that enforces an API key for internal endpoints.

    Behavior:
    - Reads `INTERNAL_API_KEY` from environment (required if used).
    - Reads `INTERNAL_API_PATH_PREFIX` env var (comma-separated) or defaults to '/internal-api/'.
    - If request.path starts with any prefix, expects header 'X-API-KEY' matching the env value.
    - If missing/invalid, returns 403.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = os.getenv('INTERNAL_API_KEY')
        prefixes = os.getenv('INTERNAL_API_PATH_PREFIX', '/internal-api/')
        # support multiple prefixes comma-separated
        self.prefixes = [p.strip() for p in prefixes.split(',') if p.strip()]

    def __call__(self, request):
        # only enforce if prefixes are configured and path matches
        if self.prefixes and any(request.path.startswith(p) for p in self.prefixes):
            # if no API key configured on server side, deny to be safe
            if not self.api_key:
                return HttpResponseForbidden('Server misconfiguration: INTERNAL_API_KEY not set')
            key = request.headers.get('X-API-KEY') or request.META.get('HTTP_X_API_KEY')
            if not key or key != self.api_key:
                return HttpResponseForbidden('Missing or invalid API key')
        return self.get_response(request)
