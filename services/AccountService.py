from models.AccountRole import AccountRole
from models.UserInformation import UserInformation
from providers.AccountDataProvider import AccountDataProvider

class AccountService:
    def __init__(self, account_provider: AccountDataProvider):
        self.account_provider = account_provider

    def get_account(self, user_id: str) -> UserInformation:
        return self.account_provider.get_user(user_id)

    def get_all_accounts(self) -> list[UserInformation]:
        return self.account_provider.get_all_users()

    def change_role(self, user_id: str, role: AccountRole) -> bool:
        return self.account_provider.update_user_role(user_id, role)