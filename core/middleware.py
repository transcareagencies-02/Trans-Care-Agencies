from django.shortcuts import redirect
from django.urls import reverse


class DashboardRedirectMiddleware:
    """Redirect the exact /dashboard path to the admin dashboard.

    Rules:
    - If request.path is /dashboard and user is authenticated:
      - Redirect to admin dashboard at /dashboard/
    - Otherwise do nothing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/dashboard' and getattr(request, 'user', None) and request.user.is_authenticated:
            return redirect(reverse('admin_dashboard'))
        return self.get_response(request)
