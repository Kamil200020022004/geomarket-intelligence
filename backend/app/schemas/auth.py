"""Schematy żądań i odpowiedzi `/auth/*`.

Kształt odpowiedzi zgodny z prototypem logowania i kodem frontendu
(`LoginDrawer.jsx`, `App.jsx`, `ResetPassword.jsx`): `{user: {id, name, email}, access_token, token_type}`.
Limity długości pól jak w prototypie.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Stabilny identyfikator UUID")
    name: str
    email: str


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)
    recaptcha_token: str | None = Field(
        default=None,
        max_length=4000,
        description="Token z widgetu Google reCAPTCHA. Wymagany, gdy serwer ma ustawiony RECAPTCHA_SECRET_KEY.",
    )

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Imię musi mieć co najmniej 2 znaki.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=254)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    user: UserOut
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    user: UserOut


class MessageResponse(BaseModel):
    message: str
