from functools import wraps
from flask import abort
from flask_login import current_user
from app.models import ExpenseGroup, GroupMember

def group_member_required(f):
    @wraps(f)
    def decorated_function(group_id, *args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        membership = GroupMember.query.filter_by(group_id=group_id, user_id=current_user.id).first()
        if not membership:
            abort(403)
        return f(group_id, *args, **kwargs)
    return decorated_function
