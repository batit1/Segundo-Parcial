import heapq
import json
import os
from datetime import datetime

ARCHIVO_DATOS = "tareas.json"

class Tarea:
    def __init__(self, nombre, prioridad, fecha_vencimiento, dependencias):
        self.nombre = nombre
        self.prioridad = prioridad
        self.fecha_vencimiento = fecha_vencimiento 
        self.dependencias = dependencias
        self.completada = False

    def es_ejecutable(self, tareas):
        return all(tareas.get(dep, {}).get("completada", False) for dep in self.dependencias)

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "prioridad": self.prioridad,
            "fecha_vencimiento": self.fecha_vencimiento,
            "dependencias": self.dependencias,
            "completada": self.completada
        }

    def cargar_desde_diccionario(self, data):
        self.nombre = data["nombre"]
        self.prioridad = data["prioridad"]
        self.fecha_vencimiento = data["fecha_vencimiento"]
        self.dependencias = data["dependencias"]
        self.completada = data.get("completada", False)


class GestorTareas:
    def __init__(self):
        self.tareas = {}
        self.cargar()

    def guardar(self):
        with open(ARCHIVO_DATOS, 'w') as f:
            json.dump({nombre: tarea.to_dict() for nombre, tarea in self.tareas.items()}, f, indent=4)

    def cargar(self):
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, 'r') as f:
                datos = json.load(f)
                for nombre, data in datos.items():
                    tarea = Tarea("", 0, "2000-01-01", [])
                    tarea.cargar_desde_diccionario(data)
                    self.tareas[nombre] = tarea

    def agregar_tarea(self, nombre, prioridad, fecha_vencimiento, dependencias):
        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not isinstance(prioridad, int):
            raise ValueError("La prioridad debe ser un número entero.")
        if nombre in self.tareas:
            raise ValueError("Ya existe una tarea con ese nombre.")
        for dep in dependencias:
            if dep not in self.tareas:
                raise ValueError(f"Dependencia '{dep}' no existe.")
        tarea = Tarea(nombre, prioridad, fecha_vencimiento, dependencias)
        self.tareas[nombre] = tarea
        self.guardar()

    def mostrar_tareas(self, orden_por='prioridad'):
        heap = []
        for tarea in self.tareas.values():
            if not tarea.completada:
                if orden_por == 'fecha':
                    clave = datetime.strptime(tarea.fecha_vencimiento, "%Y-%m-%d")
                else:
                    clave = tarea.prioridad
                heapq.heappush(heap, (clave, tarea))

        while heap:
            _, tarea = heapq.heappop(heap)
            estado = "Ejecutable" if tarea.es_ejecutable(self.tareas) else "Bloqueada"
            print(f"- {tarea.nombre} | Prioridad: {tarea.prioridad} | Vence: {tarea.fecha_vencimiento} | Estado: {estado}")

    def completar_tarea(self, nombre):
        if nombre in self.tareas and not self.tareas[nombre].completada:
            self.tareas[nombre].completada = True
            self.guardar()
        else:
            raise ValueError("Tarea no encontrada o ya completada.")

    def obtener_siguiente_tarea(self):
        heap = []
        for tarea in self.tareas.values():
            if not tarea.completada and tarea.es_ejecutable(self.tareas):
                heapq.heappush(heap, (tarea.prioridad, tarea))
        if heap:
            _, tarea = heapq.heappop(heap)
            return tarea
        else:
            return None


def menu():
    gestor = GestorTareas()
    while True:
        print("\n--- MENÚ DE GESTIÓN DE TAREAS ---")
        print("1. Añadir nueva tarea")
        print("2. Mostrar tareas pendientes")
        print("3. Completar tarea")
        print("4. Ver siguiente tarea ejecutable")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")
        try:
            if opcion == '1':
                nombre = input("Nombre de la tarea: ").strip()
                prioridad = int(input("Prioridad (entero, menor es más importante): "))
                fecha_vencimiento = input("Fecha de vencimiento (YYYY-MM-DD): ").strip()
                dependencias = input("Dependencias (nombres separados por coma, o vacío): ").strip()
                deps = [d.strip() for d in dependencias.split(",") if d.strip()] if dependencias else []
                gestor.agregar_tarea(nombre, prioridad, fecha_vencimiento, deps)
                print("Tarea añadida correctamente.")

            elif opcion == '2':
                criterio = input("¿Ordenar por 'prioridad' o 'fecha'? ").strip().lower()
                if criterio not in ['prioridad', 'fecha']:
                    criterio = 'prioridad'
                gestor.mostrar_tareas(criterio)

            elif opcion == '3':
                nombre = input("Nombre de la tarea a completar: ").strip()
                gestor.completar_tarea(nombre)
                print("Tarea marcada como completada.")

            elif opcion == '4':
                tarea = gestor.obtener_siguiente_tarea()
                if tarea:
                    print(f"➡️  Siguiente tarea ejecutable: {tarea.nombre} (Prioridad {tarea.prioridad})")
                else:
                    print("No hay tareas ejecutables disponibles.")

            elif opcion == '5':
                print("Saliendo.")
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    menu()
