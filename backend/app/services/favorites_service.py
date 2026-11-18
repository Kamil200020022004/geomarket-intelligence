"""Ulubione instrumenty użytkownika (zastępują localStorage z `frontend/src/services/favoritesService.js`)."""

import json

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Favorite

FAVORITE_TYPES = ("stock", "crypto", "macro")
# Migawka np. kryptowaluty z 7-dniową serią sparkline zajmuje kilka KB; limit chroni bazę przed nadużyciem.
MAX_ITEM_BYTES = 32 * 1024
MAX_ITEM_ID_LENGTH = 64


class InvalidFavoriteError(ValueError):
    pass


def favorite_id(item: dict) -> str:
    """Identyfikator jak `getFavoriteId()` we frontendzie: `id`, a gdy go brak — `symbol`."""
    return str(item.get("id") or item.get("symbol") or "")


def list_favorites(db: Session, user_id: str, favorite_type: str) -> list[dict]:
    rows = db.scalars(
        select(Favorite)
        .where(Favorite.user_id == user_id, Favorite.type == favorite_type)
        .order_by(Favorite.created_at, Favorite.id)
    )
    return [row.item for row in rows]


def add_favorite(db: Session, user_id: str, favorite_type: str, item: dict) -> list[dict]:
    item_id = favorite_id(item)
    if not item_id:
        raise InvalidFavoriteError("Element nie ma identyfikatora.")
    if len(item_id) > MAX_ITEM_ID_LENGTH:
        raise InvalidFavoriteError("Identyfikator elementu jest zbyt długi.")
    if len(json.dumps(item, ensure_ascii=False).encode("utf-8")) > MAX_ITEM_BYTES:
        raise InvalidFavoriteError("Element jest zbyt duży.")

    db.add(Favorite(user_id=user_id, type=favorite_type, item_id=item_id, item=item))
    try:
        db.commit()
    except IntegrityError:
        # Już jest w ulubionych (unikalność user_id, type, item_id) — jak we frontendzie: bez duplikatu, bez błędu.
        db.rollback()
    return list_favorites(db, user_id, favorite_type)


def remove_favorite(db: Session, user_id: str, favorite_type: str, item_id: str) -> list[dict]:
    db.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.type == favorite_type,
            Favorite.item_id == item_id,
        )
    )
    db.commit()
    return list_favorites(db, user_id, favorite_type)
