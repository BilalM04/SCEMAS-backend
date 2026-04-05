from flask_smorest import Blueprint
from models.ResponseSchemas import AccountSchema, ChangeRoleSchema, SuccessResponseSchema
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
        pass

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
        pass

    return blp