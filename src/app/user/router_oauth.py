from fastapi import APIRouter, Depends, Header, Path, status

from app.user.dtos.response import JwtTokenResponseDTO
from app.user.services.user_service import UserService

router = APIRouter(prefix="/oauth", tags=["Oauth 사용자 인증"])


@router.post(
    "/{social_type}/{is_auto}",
    response_model=JwtTokenResponseDTO,
    summary="소셜 로그인 & 회원가입 API",
    status_code=status.HTTP_200_OK,
)
async def oauth_login(
    social_type: str = Path(..., description="로그인 타입: 'naver' 또는 'kakao'"),
    code: str = Header(None, description="Kakao/Naver 인증 토큰"),
    user_service: UserService = Depends(),
) -> JwtTokenResponseDTO:
    return await user_service.handle_oauth_login(code=code, social_type=social_type)


@router.get("/kakao/callback")
async def kakao_callback(
    code: str,
) -> str:
    return code


@router.get("/naver/callback")
async def naver_callback(
    code: str,
) -> str:
    return code
