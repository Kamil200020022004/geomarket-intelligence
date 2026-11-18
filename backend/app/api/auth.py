"""Endpointy kont `/auth/*` (kontrakt zgodny z frontendem: LoginDrawer.jsx, App.jsx, ResetPassword.jsx)."""

from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_session, get_current_user
from app.core.config import get_settings
from app.core.rate_limit import (
    FORGOT_PASSWORD_LIMIT,
    LOGIN_LIMIT,
    REGISTER_LIMIT,
    RESET_PASSWORD_LIMIT,
    limiter,
)
from app.db.models import User, UserSession
from app.db.session import get_db
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MeResponse,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserOut,
)
from app.services import auth_service, email_service, recaptcha_service

router = APIRouter(prefix="/auth", tags=["auth"])

# Ta sama odpowiedź niezależnie od tego, czy konto istnieje (brak enumeracji kont).
FORGOT_PASSWORD_MESSAGE = "Jeśli konto istnieje, wyślemy wiadomość z linkiem resetującym."
INVALID_RESET_MESSAGE = "Link jest nieprawidłowy lub wygasł. Poproś o nowy."

ERROR_401 = {401: {"description": "Brak tokenu, token nieprawidłowy, wygasły lub unieważniony"}}
ERROR_422 = {422: {"description": "Niepoprawne dane wejściowe"}}
ERROR_429 = {429: {"description": "Przekroczony limit zapytań"}}


def _auth_response(result: auth_service.LoginResult) -> AuthResponse:
    return AuthResponse(user=UserOut.model_validate(result.user), access_token=result.access_token)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
    summary="Rejestracja konta",
    responses={
        400: {"description": "Weryfikacja reCAPTCHA nie powiodła się"},
        409: {"description": "Konto z tym adresem już istnieje"},
        **ERROR_422,
        **ERROR_429,
    },
)
@limiter.limit(REGISTER_LIMIT)
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    client_ip = request.client.host if request.client else None
    if not recaptcha_service.verify_token(body.recaptcha_token, client_ip):
        raise HTTPException(status_code=400, detail="Potwierdź, że nie jesteś robotem.")
    try:
        result = auth_service.register_user(db, body.name, body.email, body.password)
    except auth_service.EmailAlreadyRegisteredError:
        raise HTTPException(status_code=409, detail="Konto z tym adresem już istnieje.") from None
    return _auth_response(result)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Logowanie",
    responses={401: {"description": "Nieprawidłowy e-mail lub hasło"}, **ERROR_422, **ERROR_429},
)
@limiter.limit(LOGIN_LIMIT)
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        result = auth_service.login(db, body.email, body.password)
    except auth_service.InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy e-mail lub hasło.") from None
    return _auth_response(result)


@router.get("/me", response_model=MeResponse, summary="Zalogowany użytkownik", responses=ERROR_401)
def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(user=UserOut.model_validate(user))


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Wylogowanie (unieważnia token po stronie serwera)",
    responses=ERROR_401,
)
def logout(session: UserSession = Depends(get_current_session), db: Session = Depends(get_db)) -> MessageResponse:
    auth_service.logout(db, session)
    return MessageResponse(message="Wylogowano.")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Wysłanie linku resetu hasła (odpowiedź zawsze neutralna)",
    responses={**ERROR_422, **ERROR_429},
)
@limiter.limit(FORGOT_PASSWORD_LIMIT)
def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> MessageResponse:
    created = auth_service.create_password_reset(db, body.email)
    if created is not None:
        user, token = created
        settings = get_settings()
        link = f"{settings.frontend_url.rstrip('/')}/reset-password?token={quote(token)}"
        # Wysyłka po odpowiedzi: czas odpowiedzi nie zdradza, czy konto istnieje.
        background_tasks.add_task(
            email_service.send_password_reset_email, user.email, link, settings.password_reset_ttl_minutes
        )
    return MessageResponse(message=FORGOT_PASSWORD_MESSAGE)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Ustawienie nowego hasła jednorazowym tokenem",
    responses={400: {"description": INVALID_RESET_MESSAGE}, **ERROR_422, **ERROR_429},
)
@limiter.limit(RESET_PASSWORD_LIMIT)
def reset_password(request: Request, body: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    try:
        auth_service.reset_password(db, body.token, body.password)
    except auth_service.InvalidResetTokenError:
        raise HTTPException(status_code=400, detail=INVALID_RESET_MESSAGE) from None
    return MessageResponse(message="Hasło zostało zmienione. Możesz się zalogować.")
