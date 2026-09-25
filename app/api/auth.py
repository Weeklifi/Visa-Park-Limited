from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserRegisterResponse
from app.services.hierarchy import RegistrationError, register_root_user, register_user_with_referral

router = APIRouter(prefix="/auth", tags=["Auth & Registration"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        if payload.parent_referral_code is None:
            user = await register_root_user(
                db, payload.full_name, payload.email, payload.password,
                payload.phone_number, payload.nid
            )
        else:
            user = await register_user_with_referral(
                db, payload.full_name, payload.email, payload.password,
                payload.parent_referral_code, payload.phone_number, payload.nid
            )
        await db.commit()
    except RegistrationError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Email, phone number, or NID already registered"
        ) from exc

    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is inactive")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)
