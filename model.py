#model.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Mascota:
    id: Optional[int] = None
    nombre: str = ""
    especie: Optional[str] = None
    raza: Optional[str] = None
    edad: Optional[int] = None
    peso: Optional[float] = None
    fecha_ingreso: Optional[date] = None
    observaciones: Optional[str] = None