from .models.auth import get_user


def groupfinder(userid, request):
    user = get_user(userid)
    if user and user.groups:
        return ['g:%s' % g for g in user.groups.split(',')]
    else:
        return []
