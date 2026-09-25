from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20)
    nid: Optional[str] = Field(None, min_length=5, max_length=30)
    parent_referral_code: Optional[str] = Field(
        None, description="Required for all users except Root (Layer 0)"
    )


class UserRegisterResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone_number: Optional[str] = None
    nid: Optional[str] = None
    referral_code: str
    layer_level: int
    node_path: str

    model_config = {"from_attributes": True}


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone_number: Optional[str] = None
    nid: Optional[str] = None
    referral_code: str
    layer_level: int
    node_path: str
    child_count: int
    is_active: bool

    model_config = {"from_attributes": True}


class DirectReportOut(BaseModel):
    id: UUID
    full_name: str
    phone_number: Optional[str] = None
    nid: Optional[str] = None
    email: str
    referral_code: str
    layer_level: int
    child_count: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NetworkMemberOut(BaseModel):
    id: UUID
    full_name: str
    phone_number: Optional[str] = None
    layer_level: int

    model_config = {"from_attributes": True}


class TeamReportOut(BaseModel):
    direct_reports: list[DirectReportOut]
    network: list[NetworkMemberOut]
    total_team_size: int
