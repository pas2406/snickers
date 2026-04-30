from pydantic import BaseModel #classe de base Pydantic dont tous les schémas héritent. Elle valide automatiquement les types des données.
from typing import Optional # indique qu'un champ peut être None (pas obligatoire).


# ── Watch ───────────────────────────────────────────────────────────────────

class WatchCreate(BaseModel):
    brand:         str
    model:         str
    colorway:      str
    reference:     str
    category:      str
    bracelet:      str
    size_range:    Optional[str]   = None
    retail_price:  float
    resale_price:  Optional[float] = None
    release_year:  Optional[int]   = None
    description:   Optional[str]   = None
    image_url:     Optional[str]   = None
    is_available:  bool            = True


class WatchUpdate(BaseModel):
    brand:         Optional[str]   = None
    model:         Optional[str]   = None
    colorway:      Optional[str]   = None
    category:      Optional[str]   = None
    bracelet:      Optional[str]   = None
    reference:     Optional[str]   = None
    size_range:    Optional[str]   = None
    retail_price:  Optional[float] = None
    resale_price:  Optional[float] = None
    release_year:  Optional[int]   = None
    description:   Optional[str]   = None
    image_url:     Optional[str]   = None
    is_available:  Optional[bool]  = None


class WatchOut(BaseModel):
    id:            int
    brand:         str
    model:         str
    colorway:      str
    reference:     str
    category:      str
    bracelet:      str
    size_range:    Optional[str]
    retail_price:  float
    resale_price:  Optional[float]
    release_year:  Optional[int]
    description:   Optional[str]
    image_url:     Optional[str]
    is_available:  bool


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email:    str
    password: str


class UserOut(BaseModel):
    id:       int
    username: str
    email:    str
    is_admin: bool


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"