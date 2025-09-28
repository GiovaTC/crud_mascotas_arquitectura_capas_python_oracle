# repository.py
import json
from typing import List, Optional
from model import Mascota
from config import get_connection
from datetime import datetime
import os

BACKUP_FILE = "pets_backup.json"

class MascotaRepository:
    def __init__(self):
        self._use_db = True
        # probar conexión al iniciarse
        try:
            conn = get_connection()
            conn.close()
        except Exception as e:
            print(f"[WARN] No se pudo conectar a Oracle: {e}. Usando respaldo local ({BACKUP_FILE}).")
            self._use_db = False
            # asegurarse de que el archivo exista
            if not os.path.exists(BACKUP_FILE):
                with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

    # -----------------------
    # CRUD en Oracle
    # -----------------------
    def create(self, mascota: Mascota) -> Mascota:
        if not self._use_db:
            return self._create_local(mascota)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO mascotas (nombre, especie, raza, edad, peso, fecha_ingreso, observaciones)
                VALUES (:nombre, :especie, :raza, :edad, :peso, :fecha_ingreso, :observaciones)
                """
                fecha = mascota.fecha_ingreso or datetime.now()
                cur.execute(sql, {
                    "nombre": mascota.nombre,
                    "especie": mascota.especie,
                    "raza": mascota.raza,
                    "edad": mascota.edad,
                    "peso": mascota.peso,
                    "fecha_ingreso": fecha,
                    "observaciones": mascota.observaciones
                })
                # Si quieres recuperar el ID generado usando RETURNING id INTO :rid,
                # es posible usar rid = cur.var(int) y cur.execute(..., rid=rid) — ver nota al final.
            conn.commit()
            return mascota
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Al crear en Oracle: {e}. Guardando en respaldo local.")
            self._use_db = False
            return self._create_local(mascota)
        finally:
            conn.close()

    def get_all(self) -> List[Mascota]:
        if not self._use_db:
            return self._get_all_local()
        conn = get_connection()
        mascotas = []
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre, especie, raza, edad, peso, fecha_ingreso, observaciones FROM mascotas ORDER BY id")
                for r in cur:
                    m = Mascota(
                        id = int(r[0]) if r[0] is not None else None,
                        nombre = r[1],
                        especie = r[2],
                        raza = r[3],
                        edad = int(r[4]) if r[4] is not None else None,
                        peso = float(r[5]) if r[5] is not None else None,
                        fecha_ingreso = r[6],
                        observaciones = r[7]
                    )
                    mascotas.append(m)
            return mascotas
        except Exception as e:
            print(f"[ERROR] Al leer desde Oracle: {e}. Usando respaldo local.")
            self._use_db = False
            return self._get_all_local()
        finally:
            conn.close()

    def get_by_id(self, id_: int) -> Optional[Mascota]:
        if not self._use_db:
            return self._get_by_id_local(id_)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre, especie, raza, edad, peso, fecha_ingreso, observaciones FROM mascotas WHERE id = :id", {"id": id_})
                r = cur.fetchone()
                if not r:
                    return None
                return Mascota(
                    id = int(r[0]),
                    nombre = r[1],
                    especie = r[2],
                    raza = r[3],
                    edad = int(r[4]) if r[4] is not None else None,
                    peso = float(r[5]) if r[5] is not None else None,
                    fecha_ingreso = r[6],
                    observaciones = r[7]
                )
        except Exception as e:
            print(f"[ERROR] Al obtener por id desde Oracle: {e}.")
            self._use_db = False
            return self._get_by_id_local(id_)
        finally:
            conn.close()

    def update(self, mascota: Mascota) -> bool:
        if not self._use_db:
            return self._update_local(mascota)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                UPDATE mascotas
                SET nombre = :nombre, especie = :especie, raza = :raza, edad = :edad, peso = :peso, observaciones = :observaciones
                WHERE id = :id
                """
                cur.execute(sql, {
                    "nombre": mascota.nombre,
                    "especie": mascota.especie,
                    "raza": mascota.raza,
                    "edad": mascota.edad,
                    "peso": mascota.peso,
                    "observaciones": mascota.observaciones,
                    "id": mascota.id
                })
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Al actualizar en Oracle: {e}. Intentando respaldo local.")
            self._use_db = False
            return self._update_local(mascota)
        finally:
            conn.close()

    def delete(self, id_: int) -> bool:
        if not self._use_db:
            return self._delete_local(id_)
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM mascotas WHERE id = :id", {"id": id_})
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Al eliminar en Oracle: {e}. Usando respaldo local.")
            self._use_db = False
            return self._delete_local(id_)
        finally:
            conn.close()

    # -----------------------
    # Backup local JSON (respaldo)
    # -----------------------
    def _read_backup(self):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_backup(self, data):
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _create_local(self, mascota: Mascota) -> Mascota:
        data = self._read_backup()
        new_id = (max((item.get("id", 0) for item in data), default=0) + 1) if data else 1
        obj = {
            "id": new_id,
            "nombre": mascota.nombre,
            "especie": mascota.especie,
            "raza": mascota.raza,
            "edad": mascota.edad,
            "peso": mascota.peso,
            "fecha_ingreso": datetime.now().isoformat(),
            "observaciones": mascota.observaciones
        }
        data.append(obj)
        self._write_backup(data)
        mascota.id = new_id
        return mascota

    def _get_all_local(self):
        data = self._read_backup()
        result = []
        for r in data:
            m = Mascota(
                id = r.get("id"),
                nombre = r.get("nombre"),
                especie = r.get("especie"),
                raza = r.get("raza"),
                edad = r.get("edad"),
                peso = r.get("peso"),
                fecha_ingreso = r.get("fecha_ingreso"),
                observaciones = r.get("observaciones")
            )
            result.append(m)
        return result

    def _get_by_id_local(self, id_):
        data = self._read_backup()
        for r in data:
            if int(r.get("id")) == int(id_):
                return Mascota(
                    id = r.get("id"),
                    nombre = r.get("nombre"),
                    especie = r.get("especie"),
                    raza = r.get("raza"),
                    edad = r.get("edad"),
                    peso = r.get("peso"),
                    fecha_ingreso = r.get("fecha_ingreso"),
                    observaciones = r.get("observaciones")
                )
        return None

    def _update_local(self, mascota: Mascota) -> bool:
        data = self._read_backup()
        updated = False
        for i, r in enumerate(data):
            if int(r.get("id")) == int(mascota.id):
                data[i].update({
                    "nombre": mascota.nombre,
                    "especie": mascota.especie,
                    "raza": mascota.raza,
                    "edad": mascota.edad,
                    "peso": mascota.peso,
                    "observaciones": mascota.observaciones
                })
                updated = True
                break
        if updated:
            self._write_backup(data)
        return updated

    def _delete_local(self, id_) -> bool:
        data = self._read_backup()
        new = [r for r in data if int(r.get("id")) != int(id_)]
        if len(new) == len(data):
            return False
        self._write_backup(new)
        return True