# Match_Ready/context_processors.py

from .models import Coach, Player, Fan

def user_role(request):
    role = 'guest'
    is_coach = False
    team_id_for_links = None # To help generate links in base.html if needed

    if request.user.is_authenticated:
        try:
            # Check order might matter if a user could theoretically be multiple types
            if hasattr(request.user, 'coach'):
                role = 'coach'
                is_coach = True
                if request.user.coach.team:
                    team_id_for_links = request.user.coach.team.id
            elif hasattr(request.user, 'player'):
                role = 'player'
                if request.user.player.team:
                    team_id_for_links = request.user.player.team.id
            elif hasattr(request.user, 'fan'):
                role = 'fan'
                if request.user.fan.favourite_team:
                    team_id_for_links = request.user.fan.favourite_team.id
            else:
                # A logged-in user might not have a specific role profile yet
                # Or if DefaultUser is created automatically, handle that case
                 if hasattr(request.user, 'defaultuser'):
                     # This case implies they are logged in but haven't been assigned a specific role/team yet
                     role = 'member_no_role' # Or just 'member'
                 else:
                     role = 'authenticated_unknown' # Should not happen ideally

        except AttributeError:
            # This can happen if the related object (coach, player, fan) doesn't exist
            role = 'member_no_profile' # User exists, but no Player/Coach/Fan object linked

    return {
        'user_role': role,
        'is_coach': is_coach,
        'team_id_for_links': team_id_for_links, # Pass team ID for convenience
        'user': request.user # Ensure user object is always available
        }