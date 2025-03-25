from django.contrib.auth.models import User
from myapp.models import Coach, Player, Fan, UserProfile

# Example: Create a default User and UserProfile
default_user = User.objects.create(username="defaultuser")
# Assign this user to any existing Coach, Player, or Fan instance
for coach in Coach.objects.all():
    if not coach.user:
        coach.user = default_user
        coach.save()