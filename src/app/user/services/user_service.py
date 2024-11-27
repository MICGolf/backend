from fastapi import Depends, HTTPException

from app.user.dtos.auth_dto import JwtTokenResponseDTO, SocialUserInfo
from app.user.dtos.request import UserCreateRequestDTO
from app.user.models.user import User
from app.user.services.auth_service import AuthenticateService
from common.exceptions.custom_exceptions import (
    InvalidPasswordException,
    SocialLoginConflictException,
    UserNotFoundException,
)
from common.utils.sms_services import get_sms_service
from common.utils.sms_services.sms_service import SmsService


class UserService:
    def __init__(
        self,
        auth_service: AuthenticateService = Depends(),
        sms_service: SmsService = Depends(get_sms_service),
    ):
        self.auth_service = auth_service
        self.sms_service = sms_service

    async def create_user(self, user_data: UserCreateRequestDTO) -> User:

        hashed_password = self.auth_service.hash_password(plain_password=user_data.password)

        user = await User.create(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            login_id=user_data.login_id,
            password=hashed_password,
            social_login_type=user_data.social_login_type,
            social_id=user_data.social_id,
        )

        return user

    @staticmethod
    async def create_social_user(name: str, email: str, social_id: str, social_login_type: str) -> User:
        user = await User.create(
            name=name,
            email=email,
            login_id=social_id,
            password="",
            social_login_type=social_login_type,
            social_id=social_id,
        )
        return user

    @staticmethod
    async def check_login_id(login_id: str) -> None:
        user = await User.filter(login_id=login_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="This login ID is already taken.")

    async def send_sms_process(self, phone_number: str) -> None:
        verification_code = self.auth_service.generate_verification_code()
        # SMS 발송

        await self.sms_service.send_sms(phone_number, verification_code)

    async def handle_oauth_login(self, code: str, social_type: str) -> JwtTokenResponseDTO:
        access_token = await self.auth_service.get_access_token(code=code, social_type=social_type)
        social_user_info = await self.auth_service.get_social_user_info(
            access_token=access_token, social_type=social_type
        )

        user = await User.filter(email=social_user_info.email).first()

        if user:
            if user.social_login_type is None:
                user.social_id = str(social_user_info.social_id)
                user.social_login_type = social_type
                await user.save()
                return await self._handle_user(user)

            if user.social_id == str(social_user_info.social_id) and user.social_login_type == social_type:
                return await self._handle_user(user)
            else:
                raise SocialLoginConflictException(social_login_type=user.social_login_type)

        user = await self.create_social_user(
            name=social_user_info.name,
            email=social_user_info.email,
            social_id=social_user_info.social_id,
            social_login_type=social_type,
        )

        return await self._handle_user(user)

    async def _handle_user(self, user: User) -> JwtTokenResponseDTO:
        user.refresh_token_id = self.auth_service.generate_refresh_token(user_id=user.id, user_type=user.user_type)
        await user.save()

        return self._generate_jwt_response(user)

    def _generate_jwt_response(self, user: User) -> JwtTokenResponseDTO:
        return JwtTokenResponseDTO.build(
            access_token=self.auth_service.generate_access_token(
                user_id=user.id,
                user_type=user.user_type,
            ),
            user_id=user.id,
            name=user.name,
        )

    # 인증 코드 저장 (임시 저장, 만료 시간 설정)
    # await VerificationCode.create(phone_number=request.phone_number, code=verification_code)

    # def get_all_users(self) -> User | None:
    #     users = self.user_repo.get_users()
    #
    #     self._validate_user_or_raise(user=users)
    #
    #     return users
    #
    # def get_user_or_404_by_user_id(self, user_id: int) -> User:
    #     user: User | None = self.user_repo.get_user_by_id(user_id=user_id)
    #
    #     self._validate_user_or_raise(user)
    #
    #     return user
    #
    # def get_user_or_404_by_username(self, username: str) -> User:
    #     user: User | None = self.user_repo.get_user_by_username(username=username)
    #
    #     self._validate_user_or_raise(user)
    #
    #     return user
    #
    # def update_user_password_or_404(self, username: str, password: str) -> User:
    #     user: User | None = self.user_repo.get_user_by_username(username=username)
    #
    #     self._validate_user_or_raise(user)
    #
    #     new_password = self.auth_service.hash_password(plain_password=password)
    #     user.update_password(new_password=new_password)
    #     self.user_repo.save(user)
    #
    #     return user
    #
    # def delete_user_or_404(self, username: str) -> None:
    #     user: User | None = self.user_repo.get_user_by_username(username=username)
    #
    #     self._validate_user_or_raise(user)
    #
    #     self.user_repo.delete(user)
    #
    # def authenticate_user_or_404(self, username: str, password: str) -> tuple[str, str]:
    #     user: User | None = self.user_repo.get_user_by_username(username=username)
    #
    #     self._validate_user_or_raise(user)
    #
    #     if not self.auth_service.check_password(input_password=password, hashed_password=user.password):
    #         raise InvalidPasswordException()
    #
    #     access_token = self.auth_service.create_access_token(user.username)
    #     refresh_token = self.auth_service.create_refresh_token(user.username)
    #
    #     return access_token, refresh_token
    #
    # def validate_user_email_or_404(self, email: str) -> None:
    #     if self.user_repo.exist_user_email(email=email):
    #         raise HTTPException(status_code=409, detail="이미 존재하는 이메일이다")
    #
    # @staticmethod
    # def _validate_user_or_raise(user: User | None) -> None:
    #     if user is None:
    #         raise UserNotFoundException()
