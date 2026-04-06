from flask_smorest import Blueprint
from models.ResponseSchemas import AccountSchema, ChangeRoleSchema, SuccessResponseSchema
from models.AccountRole import AccountRole
from services.AccountService import AccountService
from services.OperationalService import OperationalService
from utils.Firebase import auth_required
from utils.Limiter import limiter

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
        return account_service.get_all_accounts()

    @blp.route("/role")
    @limiter.limit("60 per minute")
    @blp.response(200, AccountSchema)
    @auth_required(["admin", "operator", "public"])
    def get_account():
        """Get autheticated user's role (Admin, Operator, & Public)"""
        pass

    @blp.route("/initialize", methods=["PUT"])
    @limiter.limit("60 per minute")
    @blp.response(200, AccountSchema)
    @auth_required(["admin", "operator", "public"])
    def initialize_role():
        """Initialize autheticated user's role to public (Admin, Operator, & Public)"""
        pass
    
    @blp.route("/update", methods=["PUT"])
    @limiter.limit("60 per minute")
    @blp.arguments(ChangeRoleSchema, location="query")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin"])
    def change_role(user_id: str, role: str):
        """Change user role (Admin only)"""
        try:
            result = account_service.change_role(user_id, AccountRole(role))
            if result: return {"success": result, "message": "User role changed successfuly"}
            else: return {"success": result, "message": "Error ocurred while changing user's role"}, 500
        except Exception as e:
            print(f"Error ocurred while changing user's role")
            return {"success": False, "error": str(e)}, 500

    return blp