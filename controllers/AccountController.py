from flask_smorest import Blueprint
from flask import request
from models.ResponseSchemas import AccountSchema, ChangeRoleSchema, SuccessResponseSchema
from models.AccountRole import AccountRole
from services.AccountService import AccountService
from services.OperationalService import OperationalService
from utils.Firebase import auth_required
from utils.Limiter import limiter
from dataclasses import asdict

def create_accounts_blueprint(
    account_service: AccountService,
    operational_service: OperationalService
):
    blp = Blueprint(
        "accounts",
        "accounts",
        url_prefix="/accounts",
        description="Account endpoints"
    )

    @blp.route("/")
    @limiter.limit("60 per minute")
    @blp.response(200, AccountSchema(many=True))
    @auth_required(["admin"])
    def get_accounts():
        """Get all user accounts (Admin only)"""
        accounts = account_service.get_all_accounts()
        return [asdict(account) for account in accounts]

    @blp.route("/role")
    @limiter.limit("60 per minute")
    @blp.response(200, AccountSchema)
    @auth_required(["admin", "operator", "public"])
    def get_account():
        """Get autheticated user's role (Admin, Operator, & Public)"""
        user = request.user
        return {"user_id": user.get("uid"), "email": user.get("email"), "role": user.get("role")}


    @blp.route("/initialize", methods=["PUT"])
    @limiter.limit("60 per minute")
    @blp.response(200, AccountSchema)
    @auth_required(["admin", "operator", "public"])
    def initialize_role():
        """Initialize autheticated user's role to public (Admin, Operator, & Public)"""
        user = request.user
        id = user.get("uid")
        role = user.get("role")
        if role not in ["public", "operator", "admin"]:#needs to init
            if account_service.change_role(id, AccountRole("public")):#attempt to change role
                return {"user_id": user.get("uid"), "email": user.get("email"), "role": "public"}
            else:#if role change fails
                return {"user_id": user.get("uid"), "email": user.get("email"), "role": user.get("role")}, 500
        else:#user already initialized
            print(f"User role has already been initialized")
            return {"user_id": user.get("uid"), "email": user.get("email"), "role": user.get("role")}, 400
    
    @blp.route("/update", methods=["PUT"])
    @limiter.limit("60 per minute")
    @blp.arguments(ChangeRoleSchema, location="query")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin"])
    def change_role(args):
        """Change user role (Admin only)"""
        user_id = args.get("user_id")
        role = args.get("role")
        try:
            result = account_service.change_role(user_id, AccountRole(role))
            if result: return {"success": result, "message": "User role changed successfuly"}
            else: return {"success": result, "message": "Error ocurred while changing user's role"}, 500
        except Exception as e:
            print(f"Error ocurred while changing user's role")
            return {"success": False, "error": str(e)}, 500

    return blp