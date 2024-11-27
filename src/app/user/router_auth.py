from fastapi import APIRouter, Depends, status

from app.user.dtos.request import UserCreateRequestDTO
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
