from .models import Coach
from django.core.exceptions import ObjectDoesNotExist

def user_role(request):
    if request.user.is_authenticated:
        role = 'member'
        
    else:
        role = 'guest'
    return {'user_role': role}