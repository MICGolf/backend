class UserNotFoundException(Exception):
    def __init__(self) -> None:
        super().__init__("User not found")


class InvalidPasswordException(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid password.")


class SocialLoginConflictException(Exception):
    def __init__(self, social_login_type: str) -> None:
        self.social_login_type = social_login_type


class MaxImagesPerColorExceeded(Exception):
    def __init__(self, color_code: str, max_images: int) -> None:
        self.color_code = color_code
        self.max_images = max_images
        self.message = f"Color {color_code} has more than the allowed {max_images} images."
        super().__init__(self.message)


class MaxImageSizeExceeded(Exception):
    def __init__(self, color_code: str, max_size: int) -> None:
        self.color_code = color_code
        self.max_size = max_size
        self.message = f"Total image size for color {color_code} exceeds the {max_size // (1024 * 1024)}MB limit."
        super().__init__(self.message)
