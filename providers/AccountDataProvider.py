from firebase_admin import auth
from models.UserInformation import UserInformation
from models.AccountRole import AccountRole

class AccountDataProvider:

    def get_user(self, user_id: str) -> UserInformation | None:
        try:
            user = auth.get_user(user_id)

            claims = user.custom_claims or {}
            role_str = claims.get("role", "public")

            return UserInformation(
                user_id=user.uid,
                email=user.email,
                role=AccountRole(role_str)
            )

        except auth.UserNotFoundError:
            return None

    def get_all_users(self) -> list[UserInformation]:
        users_list = []

        page = auth.list_users()

        while page:
            for user in page.users:
                claims = user.custom_claims or {}
                role_str = claims.get("role", "public")

                users_list.append(
                    UserInformation(
                        user_id=user.uid,
                        email=user.email,
                        role=AccountRole(role_str)
                    )
                )

            page = page.get_next_page()

        return users_list

    def update_user_role(self, user_id: str, new_role: AccountRole) -> bool:
        try:
            auth.set_custom_user_claims(
                user_id,
                {"role": new_role.value}
            )
            return True

        except Exception as e:
            print("ERROR:", e)
            return False