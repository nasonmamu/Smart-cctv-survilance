from flask_login import UserMixin, current_user

class Role:
    ADMIN = 'admin'
    USER = 'user'

# Check if the current user is an admin
def is_admin():
    return hasattr(current_user, 'role') and current_user.role == Role.ADMIN
