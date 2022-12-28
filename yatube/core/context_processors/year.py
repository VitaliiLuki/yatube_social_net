from datetime import datetime


def year(request):
    """Add a variable with a current year."""
    return {
        'year': datetime.now().year
    }
