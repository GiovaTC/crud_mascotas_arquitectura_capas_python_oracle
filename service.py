#!/usr/bin/env python3
# service.py
from typing import List, Optional
from model import Mascota
from repository import MascotaRepository


class MascotaService:
    """
    Capa de servicio que maneja la lógica de negocio para las mascotas.
    Se comunica con el repositorio (Oracle o respaldo JSON).
    """

    def __init__(self):
        self.repo = MascotaRepository()

    # -----------------------
    # CRUD
    # -----------------------
    def crear_mascota(self, data: dict):
        # Convertimos el dict en objeto Mascota
        mascota = Mascota(
            id=None,
            nombre=data["nombre"],
            especie=data["especie"],
            raza=data["raza"],
            edad=data["edad"],
            peso=data["peso"],
            observaciones=data["observaciones"]
        )
        return self.repo.create(mascota)

    def listar_mascotas(self):
        return self.repo.get_all()

    def buscar_por_id(self, id):
        return self.repo.get_by_id(id)

    def actualizar_mascota(self, id, data: dict):
        mascota = Mascota(
            id=id,
            nombre=data["nombre"],
            especie=data["especie"],
            raza=data["raza"],
            edad=data["edad"],
            peso=data["peso"],
            observaciones=data["observaciones"]
        )
        return self.repo.update(mascota)

    def eliminar_mascota(self, id):
        return self.repo.delete(id)

    def buscar_por_nombre(self, nombre):
        return self.repo.search_by_name(nombre)

