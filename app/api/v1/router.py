from fastapi import APIRouter
from . import marca

api_router = APIRouter()
# NO agregar otro prefix aquí; el subrouter ya lo trae.
api_router.include_router(marca.router)  # <- sin prefix extra
