from functools import wraps

from .user import Role


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs['initiator']
        if user.role != Role.ADMIN:
            raise ValueError('Только админ может выполнять эту операцию')
        return func(*args, **kwargs)
    return wrapper
