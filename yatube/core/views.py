from django.shortcuts import render
from http import HTTPStatus


def csrf_failure(request, reason=''):
    """Rendering a page for status code 403."""
    return render(request, 'core/403csrf.html')


def page_not_found(request, exception):
    """Rendering a page for status code 404."""
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    """Rendering a page for status code 500."""
    return render(request, 'core/500.html')
