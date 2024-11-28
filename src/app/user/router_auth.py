from typing import Any

from fastapi import APIRouter, Depends, status

from app.user.dtos.request import UserCreateRequestDTO
from app.user.dtos.response import JwtTokenResponseDTO, RefreshTokenRequest, UserLoginInfoResponseDTO
from app.user.services.auth_service import AuthenticateService
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


@router.post("/verify-phone")
async def send_verification_code(
    phone_number: str,
    user_service: UserService = Depends(),
) -> dict[str, str]:
    await user_service.send_sms_process(phone_number=phone_number)
    return {"message": "Verification code sent to your phone."}


@router.post(
    "/sign-up",
    description="유저 회원가입 API입니다",
    status_code=status.HTTP_201_CREATED,
)
async def user_sign_up_handler(
    body: UserCreateRequestDTO,
    user_service: UserService = Depends(),
) -> dict[str, str]:
    await user_service.create_user(user_data=body)
    return {"message": "User created successfully."}
    # return UserResponseDto.build(user=new_user)


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
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=JwtTokenResponseDTO,
    summary="토큰 재발급 API",
    description="토큰 재발급 API입니다",
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthenticateService = Depends(),
) -> JwtTokenResponseDTO:
    return await auth_service.refresh_access_token(access_token=request.access_token)


@router.get("/protected", status_code=status.HTTP_200_OK)
async def protected_route(user_id: int = Depends(AuthenticateService().get_user_id)) -> dict[str, Any]:
    return {"message": "Access granted", "user_id": user_id}
