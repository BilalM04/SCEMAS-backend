from models.AccountRole import AccountRole
from models.UserInformation import UserInformation
from providers.AccountDataProvider import AccountDataProvider

class AccountService:
    def __init__(self, account_provider: AccountDataProvider):
        self.account_provider = account_provider

    def get_account(self, user_id: str) -> UserInformation:
        pass

    def get_all_accounts(self) -> list[UserInformation]:
        pass

    def change_role(self, user_id: str, role: AccountRole) -> bool:
        pass