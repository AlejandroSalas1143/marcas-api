from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException, Response
from app.schemas.marca import MarcaCreate, MarcaOut, MarcaUpdate
from app.storage.json_store import load, save

router = APIRouter(prefix="/marcas", tags=["marcas"])

def _utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

def _next_id(data: list[dict]) -> int:
    return max((m.get("id", 0) for m in data), default=0) + 1

def _next_contacto_id(data: list[dict]) -> int:
    max_id = 0
    for m in data:
        c = m.get("contacto")
        if c and isinstance(c.get("id"), int):
            max_id = max(max_id, c["id"])
    return max_id + 1

def _next_info_empresarial_id(data: list[dict]) -> int:
    max_id = 0
    for m in data:
        ie = m.get("info_empresarial")
        if ie and isinstance(ie.get("id"), int):
            max_id = max(max_id, ie["id"])
    return max_id + 1

def _next_titular_id(data: list[dict]) -> int:
    max_id = 0
    for m in data:
        t = m.get("titular")
        if t and isinstance(t.get("id"), int):
            max_id = max(max_id, t["id"])
    return max_id + 1

def _deep_merge(dst: dict, src: dict) -> dict:
    out = dict(dst)
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def _match_filters(m: dict, search: str | None, identificacion: str | None, clase: int | None) -> bool:
    if search:
        s = search.lower().strip()
        if s not in (m.get("nombre") or "").lower():
            return False
    if identificacion:
        tit = m.get("titular") or {}
        doc = (tit.get("identificacion") or tit.get("nit") or "")
        if identificacion.strip() not in str(doc):
            return False
    if clase is not None:
        try:
            if int(m.get("clase_niza", -1)) != int(clase):
                return False
        except (TypeError, ValueError):
            return False
    return True

def _safe_sort(data: list[dict], sort: str | None) -> list[dict]:
    if not sort:
        return data
    desc = sort.startswith("-")
    key = sort[1:] if desc else sort

    def key_fn(x: dict):
        v = x.get(key)
        if v is None:
            return (1, "")
        if key in ("clase_niza", "id"):
            try:
                return (0, int(v))
            except Exception:
                return (0, 0)
        return (0, str(v).lower())

    try:
        return sorted(data, key=key_fn, reverse=desc)
    except Exception:
        return data

@router.post("/", response_model=MarcaOut, status_code=201)
def create_marca(payload: MarcaCreate) -> MarcaOut:
    data = load()

    item = payload.model_dump()
    item["id"] = _next_id(data)  # id de la marca
    now = _utcnow_iso()
    item["creado_en"] = now
    item["actualizado_en"] = now

    # Asignar id a titular
    tit = item.get("titular")
    if tit and "id" not in tit:
        tit["id"] = _next_titular_id(data)

    # Asignar id a contacto top-level
    if item.get("contacto") and "id" not in item["contacto"]:
        item["contacto"]["id"] = _next_contacto_id(data)

    # Asignar id a info_empresarial top-level
    if item.get("info_empresarial") and "id" not in item["info_empresarial"]:
        item["info_empresarial"]["id"] = _next_info_empresarial_id(data)

    data.append(item)
    save(data)
    return MarcaOut.model_validate(item)

@router.get("/", response_model=List[MarcaOut])
def list_marcas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = Query(None),
    identificacion: Optional[str] = Query(None),
    clase_niza: Optional[int] = Query(None, alias="clase"),
    sort: Optional[str] = Query(None),
) -> List[MarcaOut]:
    data = load()
    filtered = [m for m in data if _match_filters(m, search, identificacion, clase_niza)]
    ordered = _safe_sort(filtered, sort)
    page = ordered[skip : skip + limit]
    return [MarcaOut.model_validate(m) for m in page]

@router.get("/{marca_id}", response_model=MarcaOut)
def get_marca(marca_id: int) -> MarcaOut:
    for m in load():
        if m.get("id") == marca_id:
            return MarcaOut.model_validate(m)
    raise HTTPException(404, "Marca no encontrada")

@router.put("/{marca_id}", response_model=MarcaOut)
def update_marca(marca_id: int, payload: MarcaUpdate) -> MarcaOut:
    data = load()
    for i, m in enumerate(data):
        if m.get("id") == marca_id:
            patch = payload.model_dump(exclude_unset=True)
            updated = _deep_merge(m, patch)
            updated["id"] = marca_id
            updated["actualizado_en"] = _utcnow_iso()
            data[i] = updated
            save(data)
            return MarcaOut.model_validate(updated)
    raise HTTPException(404, "Marca no encontrada")

@router.delete("/{marca_id}", status_code=204)
def delete_marca(marca_id: int):
    data = load()
    new_data = [m for m in data if m.get("id") != marca_id]
    if len(new_data) == len(data):
        raise HTTPException(404, "Marca no encontrada")
    save(new_data)
    return Response(status_code=204)
