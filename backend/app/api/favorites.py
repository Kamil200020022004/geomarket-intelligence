"""Endpointy ulubionych `/api/favorites/{type}`.

Odpowiadają funkcjom `getFavorites`, `addFavorite`, `removeFavorite` z `favoritesService.js`:
każda zwraca aktualną tablicę elementów danego typu. Właściciel zawsze z tokenu.
"""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.services import favorites_service

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

FavoriteType = Literal["stock", "crypto", "macro"]
ERRORS = {401: {"description": "Wymagane logowanie"}, 422: {"description": "Nieprawidłowy typ lub element"}}


@router.get("/{favorite_type}", summary="Lista ulubionych danego typu", responses=ERRORS)
def get_favorites(
    favorite_type: FavoriteType,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return favorites_service.list_favorites(db, user.id, favorite_type)


@router.post("/{favorite_type}", summary="Dodanie elementu (migawki obiektu) do ulubionych", responses=ERRORS)
def add_favorite(
    favorite_type: FavoriteType,
    item: Annotated[
        dict[str, Any],
        Body(examples=[{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 97000.5}]),
    ],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    try:
        return favorites_service.add_favorite(db, user.id, favorite_type, item)
    except favorites_service.InvalidFavoriteError as error:
        raise HTTPException(status_code=422, detail=str(error)) from None


@router.delete("/{favorite_type}/{item_id}", summary="Usunięcie elementu z ulubionych", responses=ERRORS)
def remove_favorite(
    favorite_type: FavoriteType,
    item_id: Annotated[str, Path(max_length=64)],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return favorites_service.remove_favorite(db, user.id, favorite_type, item_id)
