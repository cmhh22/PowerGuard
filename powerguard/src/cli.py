import asyncio
import os
from datetime import datetime
from services import load_outages, save_outages
from utils import filter_pending, format_outages, format_csv
from models import Outage
from colorama import init, Fore, Style

init(autoreset=True)

OPCIONES_MENU = {
    '1': 'Registrar nuevo apagón',
    '2': 'Marcar apagón como resuelto',
    '3': 'Ver apagones pendientes',
    '4': 'Generar reporte CSV',
    '5': 'Filtrar apagones',
    '6': 'Editar apagón',
    '7': 'Eliminar apagón',
    '8': 'Ver estadísticas',
    '9': 'Salir',
}

def imprimir_menu():
    print(Fore.MAGENTA + Style.BRIGHT + "\n--- PowerGuard ---")
    for clave, valor in OPCIONES_MENU.items():
        print(Fore.BLUE + f"{clave}. {valor}")

def obtener_siguiente_id(apagones):
    ids_existentes = {a.id for a in apagones}
    siguiente_id = 1
    while siguiente_id in ids_existentes:
        siguiente_id += 1
    return siguiente_id

async def main():
    os.makedirs('data', exist_ok=True)
    apagones = await load_outages()

    while True:
        imprimir_menu()
        opcion = input(Fore.GREEN + "Seleccione una opción: ").strip()

        if opcion == '1':
            zona = input(Fore.GREEN + "Ingrese la zona afectada: ").strip().upper()
            if not zona:
                print(Fore.RED + "✖ La zona no puede estar vacía.")
                continue

            duracion = input(Fore.GREEN + "Duración estimada (minutos): ").strip()
            if not duracion.isdigit() or int(duracion) <= 0:
                print(Fore.RED + "✖ La duración debe ser un entero positivo.")
                continue

            apagon = Outage(
                id=obtener_siguiente_id(apagones),
                zone=zona,
                start_time=datetime.now(),
                duration_estimated=int(duracion)
            )
            apagones.append(apagon)
            await save_outages(apagones)
            print(Fore.GREEN + "✔ Apagón registrado con éxito.")

        elif opcion == '2':
            try:
                pid = int(input(Fore.GREEN + "Ingrese el ID del apagón para marcar como resuelto: ").strip())
            except ValueError:
                print(Fore.RED + "✖ ID no válido.")
                continue
            for apagon in apagones:
                if apagon.id == pid and not apagon.resolved:
                    apagon.resolved = True
                    apagon.resolved_time = datetime.now()
                    await save_outages(apagones)
                    print(Fore.GREEN + "✔ Apagón marcado como resuelto.")
                    break
            else:
                print(Fore.RED + "✖ ID no encontrado o ya resuelto.")

        elif opcion == '3':
            pendientes = filter_pending(apagones)
            salida = format_outages(pendientes) or (Fore.YELLOW + "No hay apagones pendientes.")
            print(salida)

        elif opcion == '4':
            datos_csv = format_csv(apagones)
            with open('reporte_apagones.csv', 'w') as f:
                f.write(datos_csv)
            print(Fore.GREEN + "✔ Reporte CSV generado: reporte_apagones.csv")

        elif opcion == '5':
            print(Fore.CYAN + "\n--- Filtrar Apagones ---")
            zona = input(Fore.GREEN + "Ingrese la zona para filtrar (deje en blanco para todo): ").strip().upper()
            estado = input(Fore.GREEN + "¿Filtrar por estado? (pendientes/resueltos/todos): ")

            filtrados = apagones
            if zona:
                filtrados = [a for a in filtrados if a.zone == zona]
            if estado == 'pendientes':
                filtrados = [a for a in filtrados if not a.resolved]
            elif estado == 'resueltos':
                filtrados = [a for a in filtrados if a.resolved]
            salida = format_outages(filtrados) or (Fore.YELLOW + "No se encontraron apagones con esos filtros.")
            print(salida)

        elif opcion == '6':
            try:
                pid = int(input(Fore.GREEN + "Ingrese el ID del apagón para editar: ").strip())
            except ValueError:
                print(Fore.RED + "✖ ID no válido.")
                continue
            for apagon in apagones:
                if apagon.id == pid:
                    print(Fore.YELLOW + f"Editando apagón {pid} (Zona: {apagon.zone}, Duración: {apagon.duration_estimated} min)")
                    nueva_zona = input(Fore.GREEN + f"Nueva zona (dejar en blanco para mantener '{apagon.zone}'): ").strip().upper()
                    if nueva_zona:
                        apagon.zone = nueva_zona
                    nueva_duracion = input(Fore.GREEN + f"Nueva duración (dejar en blanco para mantener '{apagon.duration_estimated}'): ").strip()
                    if nueva_duracion:
                        if nueva_duracion.isdigit() and int(nueva_duracion) > 0:
                            apagon.duration_estimated = int(nueva_duracion)
                        else:
                            print(Fore.RED + "✖ La duración debe ser un entero positivo.")
                            continue
                    await save_outages(apagones)
                    print(Fore.GREEN + "✔ El apagón se actualizó con éxito.")
                    break
            else:
                print(Fore.RED + "✖ ID no encontrado.")

        elif opcion == '7':
            try:
                pid = int(input(Fore.GREEN + "Ingrese el ID del apagón para eliminar: ").strip())
            except ValueError:
                print(Fore.RED + "✖ ID no válido.")
                continue
            for i, apagon in enumerate(apagones):
                if apagon.id == pid:
                    confirmar = input(Fore.RED + f"¿Está seguro de que desea eliminar el apagón {pid}? (s/n): ").strip().lower()
                    if confirmar == 's':
                        apagones.pop(i)
                        await save_outages(apagones)
                        print(Fore.GREEN + "✔ El apagón se eliminó con éxito.")
                    else:
                        print(Fore.YELLOW + "Eliminación cancelada.")
                    break
            else:
                print(Fore.RED + "✖ ID no encontrado.")

        elif opcion == '8':
            total = len(apagones)
            pendientes = len([a for a in apagones if not a.resolved])
            resueltos = len([a for a in apagones if a.resolved])
            zonas = {}
            for a in apagones:
                zonas[a.zone] = zonas.get(a.zone, 0) + 1
            duracion_promedio = (
                sum(a.duration_estimated for a in apagones if a.duration_estimated) / total
                if total > 0 else 0
            )
            print(Fore.CYAN + "\n--- Estadísticas de apagones ---")
            print(Fore.YELLOW + f"Apagones totales: {total}")
            print(Fore.YELLOW + f"Apagones pendientes: {pendientes}")
            print(Fore.YELLOW + f"Apagones resueltos: {resueltos}")
            print(Fore.YELLOW + f"Duración promedio estimada: {duracion_promedio:.1f} min")
            print(Fore.YELLOW + "Apagones por zona:")
            for zona, cantidad in zonas.items():
                print(Fore.YELLOW + f"  Zona {zona}: {cantidad}")

        elif opcion == '9':
            print(Fore.MAGENTA + "👋 Saliendo de PowerGuard. ¡Adiós!")
            break

        else:
            print(Fore.RED + "✖ Opción no válida. Por favor, inténtelo de nuevo.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"\nOcurrió un error inesperado: {e}")
        input(Fore.YELLOW + "\nPresiona Enter para salir...")
