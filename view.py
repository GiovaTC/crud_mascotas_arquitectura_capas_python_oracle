# view.py
from service import MascotaService
from tabulate import tabulate

svc = MascotaService()

def input_non_empty(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v

def mostrar_menu():
    print("\n=== Almacén de Mascotas ===")
    print("1) Listar mascotas")
    print("2) Crear mascota")
    print("3) Ver mascota por ID")
    print("4) Actualizar mascota")
    print("5) Eliminar mascota")
    print("0) Salir")

def listar():
    mascotas = svc.listar_mascotas()
    if not mascotas:
        print("No hay mascotas registradas.")
        return
    table = []
    for m in mascotas:
        table.append([m.id, m.nombre, m.especie, m.raza, m.edad, m.peso, getattr(m, "fecha_ingreso", "")])
    print(tabulate(table, headers=["ID","Nombre","Especie","Raza","Edad","Peso","Fecha ingreso"], tablefmt="grid"))

def crear():
    print("Crear nueva mascota:")
    nombre = input_non_empty("Nombre: ")
    especie = input("Especie: ").strip()
    raza = input("Raza: ").strip()
    edad = input("Edad (número): ").strip()
    peso = input("Peso (kg): ").strip()
    obs = input("Observaciones: ").strip()
    data = {
        "nombre": nombre,
        "especie": especie or None,
        "raza": raza or None,
        "edad": int(edad) if edad else None,
        "peso": float(peso) if peso else None,
        "observaciones": obs or None
    }
    m = svc.crear_mascota(data)
    print(f"Mascota creada (id={m.id}).")

def ver_por_id():
    id_ = input_non_empty("ID de la mascota: ")
    m = svc.obtener_mascota(int(id_))
    if not m:
        print("Mascota no encontrada.")
        return
    print("Detalles:")
    for k, v in m.__dict__.items():
        print(f"  {k}: {v}")

def actualizar():
    id_ = input_non_empty("ID a actualizar: ")
    m = svc.obtener_mascota(int(id_))
    if not m:
        print("No existe mascota con ese ID.")
        return
    print("Dejar vacío para mantener el valor actual.")
    nombre = input(f"Nombre [{m.nombre}]: ").strip() or m.nombre
    especie = input(f"Especie [{m.especie}]: ").strip() or m.especie
    raza = input(f"Raza [{m.raza}]: ").strip() or m.raza
    edad = input(f"Edad [{m.edad}]: ").strip()
    peso = input(f"Peso [{m.peso}]: ").strip()
    obs = input(f"Observaciones [{m.observaciones}]: ").strip() or m.observaciones
    data = {
        "nombre": nombre,
        "especie": especie,
        "raza": raza,
        "edad": int(edad) if edad else m.edad,
        "peso": float(peso) if peso else m.peso,
        "observaciones": obs
    }
    ok = svc.actualizar_mascota(int(id_), data)
    print("Actualizado." if ok else "No se pudo actualizar.")

def eliminar():
    id_ = input_non_empty("ID a eliminar: ")
    ok = svc.eliminar_mascota(int(id_))
    print("Eliminado." if ok else "No encontrado o no se pudo eliminar.")

def run_cli():
    while True:
        mostrar_menu()
        op = input("Selecciona opción: ").strip()
        if op == "1":
            listar()
        elif op == "2":
            crear()
        elif op == "3":
            ver_por_id()
        elif op == "4":
            actualizar()
        elif op == "5":
            eliminar()
        elif op == "0":
            print("Saliendo. ¡Hasta luego!")
            break
        else:
            print("Opción inválida.")