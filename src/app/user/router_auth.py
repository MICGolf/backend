from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status

from app.user.dtos.request import (
    PasswordResetRequestDTO,
    ResetPasswordRequest,
    UserCreateRequestDTO,
    UserLoginRequestDTO,
)
from app.user.dtos.response import JwtTokenResponseDTO, RefreshTokenRequest, UserLoginInfoResponseDTO
from app.user.services.auth_service import AuthenticateService, get_token_from_header
from app.user.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["사용자 인증"])


@router.get(
    "/check-login-id",
    status_code=status.HTTP_200_OK,
)
async def check_login_id(
    login_id: str,
    user_service: UserService = Depends(),
) -> dict[str, str]:
    await user_service.check_login_id(login_id=login_id)
    return {"message": "Login ID is available."}


@router.post(
    "/verify-phone",
    deprecated=True,
)
async def send_verification_code(
    phone_number: str,
    user_service: UserService = Depends(),
) -> dict[str, str]:
    await user_service.send_sms_process(phone_number=phone_number)
    return {"message": "Verification code sent to your phone."}


@router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    summary="유저 회원가입 API",
    description="유저 회원가입 API입니다",
)
async def user_sign_up_handler(
    body: UserCreateRequestDTO,
    user_service: UserService = Depends(),
) -> dict[str, str]:
    await user_service.create_user(user_data=body)
    return {"message": "User created successfully."}


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=JwtTokenResponseDTO,
    summary="일반 로그인 API",
    description="일반 로그인 API입니다",
)
async def user_login_handler(
    body: UserLoginRequestDTO,
    user_service: UserService = Depends(),
) -> JwtTokenResponseDTO:
    return await user_service.handle_login(login_id=body.login_id, password=body.password)


@router.get(
    "/find-id",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginInfoResponseDTO,
    summary="사용자 아이디 조회 API",
    description="로그인 Id 조회 API입니다",
)
async def find_login_id_handler(
    name: str,
    email: str,
    user_service: UserService = Depends(),
) -> UserLoginInfoResponseDTO:
    return await user_service.find_user_login_id_by_name_and_email(name=name, email=email)


@router.post(
    "/request-password-reset",
    status_code=status.HTTP_200_OK,
    summary="사용자 비밀번호 초기화 요청 API",
    description="비밀번호 초기화 요청 API입니다",
)
async def reset_password_request_handler(
    request: Request,
    body: PasswordResetRequestDTO,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(),
) -> dict[str, str]:
    background_tasks.add_task(
        user_service.send_password_reset_mail,
        body.name,
        body.login_id,
        str(request.base_url),
    )
    return {"message": "Password reset email sent."}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="사용자 비밀번호 초기화 API",
    description="비밀번호 초기화 API입니다",
)
async def reset_password_handler(
    request: ResetPasswordRequest,
    user_service: UserService = Depends(),
) -> dict[str, str]:
    await user_service.reset_password(request.token, request.new_password)
    return {"message": "Password reset successfully."}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=JwtTokenResponseDTO,
    summary="토큰 재발급 API",
    description="토큰 재발급 API입니다",
)
async def refresh_token(
    access_token: str = Depends(get_token_from_header),
    auth_service: AuthenticateService = Depends(),
) -> JwtTokenResponseDTO:
    return await auth_service.refresh_access_token(access_token=access_token)


@router.get(
    "/protected",
    status_code=status.HTTP_200_OK,
    summary="토큰 정보 추출 테스트 API",
    description="토큰 정보 추출 테스트 API",
)
async def protected_route(
    user_id: int = Depends(AuthenticateService().get_user_id),
) -> dict[str, Any]:
    return {"message": "Access granted", "user_id": user_id}
