from flask_smorest import Blueprint
from models.ResponseSchemas import AccountSchema, ChangeRoleSchema, SuccessResponseSchema
from services.AccountService import AccountService
from services.OperationalService import OperationalService
from utils.firebase import auth_required

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
    @blp.response(200, AccountSchema(many=True))
    @auth_required(["admin"])
    def get_accounts():
        """Get all user accounts (Admin only)"""
        pass
    
    @blp.route("/update", methods=["PUT"])
    @blp.arguments(ChangeRoleSchema, location="query")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin"])
    
    def change_role(user_id: str, role: str):
        """Change user role (Admin only)"""
        pass

    return blp