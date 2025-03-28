from Match_Ready.views import find_default_user
from Match_Ready.models import Coach

def custom_context(request):
    if request.user.is_authenticated:
        role = find_default_user(request,request.user)
        if isinstance(role,Coach):
            return {'user_is_coach':True}
        
    
    return {'user_is_coach':False}