from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from database import get_db
from schemas import WatchCreate, WatchUpdate, WatchOut

router = APIRouter()


def _row_to_dict(row) -> dict:
    """Convertit un sqlite3.Row en dict pour Pydantic."""
    return dict(row)


# ── Lister / Filtrer ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[WatchOut])
def list_watches(
    brand:     Optional[str]   = Query(None),
    category:  Optional[str]   = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
):
    """
    SELECT avec filtres dynamiques construits proprement
    via des paramètres positionnels — jamais de f-string dans le SQL.
    """
    sql    = "SELECT * FROM watches WHERE 1=1"
    params: list = []

    if brand:
        sql += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    if category:
        sql += " AND category LIKE ?"
        params.append(f"%{category}%")
    if min_price is not None:
        sql += " AND retail_price >= ?"
        params.append(min_price)
    if max_price is not None:
        sql += " AND retail_price <= ?"
        params.append(max_price)

    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()

    return [_row_to_dict(r) for r in rows]


# ── Rechercher ────────────────────────────────────────────────────────────────
# term = f"%{q}%" construit le terme de recherche pour le LIKE en SQL.
# % est un joker SQL qui signifie "n'importe quels caractères".

@router.get("/search", response_model=List[WatchOut])
def search_watches(q: str = Query(..., min_length=1)):
    """
    Recherche plein-texte sur brand, model, colorway.
    Le même paramètre ? est réutilisé trois fois.
    """
    sql = """
        SELECT * FROM watches
        WHERE brand    LIKE ?
           OR model    LIKE ?
           OR colorway LIKE ?
    """
    term = f"%{q}%"

    with get_db() as conn:
        rows = conn.execute(sql, [term, term, term]).fetchall()

    return [_row_to_dict(r) for r in rows]


# ── Comparer ──────────────────────────────────────────────────────────────────

@router.get("/compare", response_model=List[WatchOut])
def compare_watches(ids: str = Query(..., description="IDs séparés par virgule : 1,2")):
    """
    SELECT avec IN (?, ?, ...) — le nombre de placeholders
    est généré dynamiquement selon la liste d'IDs.
    """
    try:
        id_list = [int(i) for i in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs invalides")

    if len(id_list) < 2:
        raise HTTPException(status_code=400, detail="Fournir au moins 2 IDs")

    placeholders = ", ".join("?" * len(id_list))
    sql = f"SELECT * FROM watches WHERE id IN ({placeholders})"

    with get_db() as conn:
        rows = conn.execute(sql, id_list).fetchall()

    if len(rows) < 2:
        raise HTTPException(status_code=404, detail="Un ou plusieurs IDs introuvables")

    return [_row_to_dict(r) for r in rows]


# ── Voir une montre ───────────────────────────────────────────────────────────

@router.get("/{watch_id}", response_model=WatchOut)
def get_watch(watch_id: int):
    """SELECT * FROM watches WHERE id = ?"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM watches WHERE id = ?", [watch_id]
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Watch introuvable")

    return _row_to_dict(row)


# ── Créer ─────────────────────────────────────────────────────────────────────

@router.post("/", response_model=WatchOut, status_code=201)
def create_watch(payload: WatchCreate):
    """
    INSERT avec tous les champs nommés.
    On vérifie d'abord que la référence n'existe pas (UNIQUE).
    """
    sql_check = "SELECT id FROM watches WHERE reference = ?"
    sql_insert = """
        INSERT INTO watches
            (brand, model, colorway, bracelet, reference, category,
             size_range, retail_price, resale_price,
             release_year, description, image_url, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_db() as conn:
        if conn.execute(sql_check, [payload.reference]).fetchone():
            raise HTTPException(status_code=409, detail="Référence déjà existante")

        cursor = conn.execute(sql_insert, [
            payload.brand, payload.model, payload.colorway, payload.bracelet,
            payload.reference, payload.category, payload.size_range,
            payload.retail_price, payload.resale_price,
            payload.release_year, payload.description,
            payload.image_url, int(payload.is_available),
        ])
        new_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM watches WHERE id = ?", [new_id]).fetchone()

    return _row_to_dict(row)


# ── Modifier ──────────────────────────────────────────────────────────────────

@router.patch("/{watch_id}", response_model=WatchOut)
def update_watch(watch_id: int, payload: WatchUpdate):
    """
    UPDATE dynamique : on ne met à jour que les champs fournis.
    Construction du SET clause colonne par colonne.
    """
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="Aucun champ à modifier")

    set_clause = ", ".join(f"{col} = ?" for col in fields)
    values     = list(fields.values()) + [watch_id]
    sql        = f"UPDATE watches SET {set_clause} WHERE id = ?"

    with get_db() as conn:
        cursor = conn.execute(sql, values)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="watch introuvable")
        row = conn.execute("SELECT * FROM watches WHERE id = ?", [watch_id]).fetchone()

    return _row_to_dict(row)


# ── Supprimer ─────────────────────────────────────────────────────────────────

@router.delete("/{watch_id}", status_code=204)
def delete_watch(watch_id: int):
    """DELETE FROM watches WHERE id = ?"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM watches WHERE id = ?", [watch_id])
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="watch introuvable")
