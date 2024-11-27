class UserNotFoundException(Exception):
    def __init__(self) -> None:
        super().__init__("User not found")


class InvalidPasswordException(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid password.")


class SocialLoginConflictException(Exception):
    def __init__(self, social_login_type: str):
        self.social_login_type = social_login_type
