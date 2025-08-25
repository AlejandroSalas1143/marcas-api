from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from datetime import datetime

TipoPersona = Literal["Natural", "Juridica"]
Sector = Literal["Comercio", "Manufactura", "Servicios"]

class TitularIn(BaseModel):
    tipo_persona: TipoPersona
    # Natural
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    identificacion: Optional[str] = None
    # Jurídica
    razon_social: Optional[str] = None
    nit: Optional[str] = None
    rep_legal_nombres: Optional[str] = None
    rep_legal_apellidos: Optional[str] = None
    rep_legal_identificacion: Optional[str] = None

class InfoEmpresarialIn(BaseModel):
    sector: Sector
    ingresos_anuales: float = 0

class ContactoIn(BaseModel):
    nombres: str
    apellidos: str
    email: EmailStr
    telefono: str
    direccion: str
    pais: str
    ciudad: str

class MarcaCreate(BaseModel):
    nombre: str
    clase_niza: int
    titular_id: Optional[int] = None
    titular: Optional[TitularIn] = None
    info_empresarial: Optional[InfoEmpresarialIn] = None
    contacto: Optional[ContactoIn] = None

    @field_validator("nombre")
    @classmethod
    def strip(cls, v: str) -> str:
        return v.strip()

    @field_validator("clase_niza")
    @classmethod
    def validar_niza(cls, v: int) -> int:
        if not (1 <= v <= 45):
            raise ValueError("clase_niza debe estar entre 1 y 45")
        return v

class ContactoOut(ContactoIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

class InfoEmpresarialOut(InfoEmpresarialIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TitularOut(TitularIn):
    id: int
    contacto: Optional[ContactoOut] = None
    info_empresarial: Optional[InfoEmpresarialOut] = None
    model_config = ConfigDict(from_attributes=True)

class MarcaOut(BaseModel):
    id: int
    nombre: str
    clase_niza: int
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None
    titular: TitularOut
    model_config = ConfigDict(from_attributes=True)

class TitularUpdate(TitularIn): pass
class InfoEmpresarialUpdate(InfoEmpresarialIn): pass
class ContactoUpdate(ContactoIn): pass

class MarcaUpdate(BaseModel):
    nombre: Optional[str] = None
    clase_niza: Optional[int] = None
    titular_id: Optional[int] = None
    titular: Optional[TitularUpdate] = None
    contacto: Optional[ContactoUpdate] = None
    info_empresarial: Optional[InfoEmpresarialUpdate] = None
