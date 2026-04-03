from firebase_admin import auth
from functools import wraps
from flask import request

def auth_required(roles=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", None)

            if not auth_header:
                return {"message": "Missing token"}, 401

            token = auth_header.split(" ")[1]

            try:
                decoded = auth.verify_id_token(token)
                request.user = decoded
            except Exception:
                return {"message": "Invalid token"}, 401

            user_role = decoded.get("role", "public")

            if roles and user_role not in roles:
                return {"message": "Forbidden"}, 403

            return f(*args, **kwargs)

        return decorated
    return wrapper