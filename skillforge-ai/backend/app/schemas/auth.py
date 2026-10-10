"""Auth and user Pydantic schemas (never include password hashes)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role: RoleSummary
    is_active: bool
    last_login_at: datetime | None = None
    email_verified_at: datetime | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=8, max_length=512)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=8, max_length=512)
    password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str
