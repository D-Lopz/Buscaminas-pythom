"""
Estructura de Datos - Entrega Final
David López y Jhon Alexis
Back-end
"""
import random
from typing import List, Tuple, Optional

# ESTRUCTURA 1: LISTA ENLAZADA CIRCULAR

class NodoCelda:
    """Nodo para lista enlazada que representa una celda del tablero"""

    def __init__(self, fila: int, col: int):
        self.fila = fila
        self.col = col
        self.tiene_mina = False
        self.revelada = False
        self.marcada = False
        self.minas_adyacentes = 0
        self.siguiente = None


class ListaEnlazadaCircular:
    """Lista enlazada circular para almacenar las celdas del tablero"""

    def __init__(self):
        self.cabeza = None
        self.cantidad = 0

    def agregar(self, fila: int, col: int) -> NodoCelda:
        nuevo = NodoCelda(fila, col)
        if not self.cabeza:
            self.cabeza = nuevo
            nuevo.siguiente = self.cabeza
        else:
            actual = self.cabeza
            while actual.siguiente != self.cabeza:
                actual = actual.siguiente
            actual.siguiente = nuevo
            nuevo.siguiente = self.cabeza
        self.cantidad += 1
        return nuevo

    def buscar(self, fila: int, col: int) -> Optional[NodoCelda]:
        if not self.cabeza:
            return None
        actual = self.cabeza

        while True:
            if actual.fila == fila and actual.col == col:
                return actual
            actual = actual.siguiente
            if actual == self.cabeza:
                break
        return None

# ESTRUCTURA 2: PILA (para deshacer jugadas)

class NodoPila:
    """Nodo para la pila de movimientos"""

    def __init__(self, fila: int, col: int, accion: str):
        self.fila = fila
        self.col = col
        self.accion = accion
        self.siguiente = None


class Pila:
    """Pila para almacenar el historial de movimientos"""

    def __init__(self):
        self.tope = None
        self.tamaño = 0

    def apilar(self, fila: int, col: int, accion: str):
        nuevo = NodoPila(fila, col, accion)
        nuevo.siguiente = self.tope
        self.tope = nuevo
        self.tamaño += 1

    def desapilar(self) -> Optional[Tuple[int, int, str]]:
        if self.esta_vacia():
            return None
        nodo = self.tope
        self.tope = self.tope.siguiente
        self.tamaño -= 1
        return (nodo.fila, nodo.col, nodo.accion)

    def esta_vacia(self) -> bool:
        return self.tope is None


# ESTRUCTURA 3: COLA (para expansión de celdas)

class NodoCola:
    """Nodo para la cola de procesamiento"""

    def __init__(self, fila: int, col: int):
        self.fila = fila
        self.col = col
        self.siguiente = None


class Cola:
    """Cola para procesar celdas adyacentes en expansión automática"""

    def __init__(self):
        self.frente = None
        self.final = None
        self.tamaño = 0

    def encolar(self, fila: int, col: int):
        nuevo = NodoCola(fila, col)
        if self.esta_vacia():
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo
        self.tamaño += 1

    def desencolar(self) -> Optional[Tuple[int, int]]:
        if self.esta_vacia():
            return None
        nodo = self.frente
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self.tamaño -= 1
        return (nodo.fila, nodo.col)

    def esta_vacia(self) -> bool:
        return self.frente is None


# CLASE PRINCIPAL DEL JUEGO

class Buscaminas:
    """Clase principal que gestiona la lógica del juego Buscaminas"""

    def __init__(self, filas: int = 10, columnas: int = 10, num_minas: int = 15):
        """
        Inicializa el juego
        Args:
            filas: número de filas del tablero
            columnas: número de columnas del tablero
            num_minas: cantidad de minas a colocar
        """
        self.filas = filas
        self.columnas = columnas
        self.num_minas = num_minas
        self.tablero = ListaEnlazadaCircular()
        self.historial = Pila()
        self.juego_terminado = False
        self.victoria = False
        self.celdas_reveladas = 0

        # Crear matriz auxiliar para acceso rápido
        self.matriz = [[None for _ in range(columnas)] for _ in range(filas)]

        # Inicializar tablero
        self._inicializar_tablero()
        self._colocar_minas()
        self._calcular_numeros()

    def _inicializar_tablero(self):
        """Crea todas las celdas del tablero usando lista enlazada circular"""
        for i in range(self.filas):
            for j in range(self.columnas):
                nodo = self.tablero.agregar(i, j)
                self.matriz[i][j] = nodo

    def _colocar_minas(self):
        """Coloca minas aleatoriamente en el tablero"""
        minas_colocadas = 0
        while minas_colocadas < self.num_minas:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            celda = self.matriz[fila][col]

            if not celda.tiene_mina:
                celda.tiene_mina = True
                minas_colocadas += 1

    def _calcular_numeros(self):
        """Calcula el número de minas adyacentes para cada celda"""
        direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for i in range(self.filas):
            for j in range(self.columnas):
                celda = self.matriz[i][j]
                if not celda.tiene_mina:
                    contador = 0
                    for df, dc in direcciones:
                        ni, nj = i + df, j + dc
                        if 0 <= ni < self.filas and 0 <= nj < self.columnas:
                            if self.matriz[ni][nj].tiene_mina:
                                contador += 1
                    celda.minas_adyacentes = contador

    def revelar_celda(self, fila: int, col: int) -> dict:
        """
        Revela una celda y expande automáticamente si es necesario
        Returns: dict con información del resultado
        """
        resultado = {
            'valido': True,
            'game_over': False,
            'victoria': False,
            'celdas_reveladas': []
        }

        if self.juego_terminado:
            resultado['valido'] = False
            return resultado

        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            resultado['valido'] = False
            return resultado

        celda = self.matriz[fila][col]

        if celda.revelada or celda.marcada:
            resultado['valido'] = False
            return resultado

        # Guardar en historial
        self.historial.apilar(fila, col, "revelar")

        # Si hay mina, juego terminado
        if celda.tiene_mina:
            celda.revelada = True
            self.juego_terminado = True
            self.victoria = False
            resultado['game_over'] = True
            resultado['celdas_reveladas'].append((fila, col))
            return resultado

        # Usar COLA para expansión automática (BFS)
        cola = Cola()
        cola.encolar(fila, col)
        visitados = set()

        while not cola.esta_vacia():
            f, c = cola.desencolar()

            if (f, c) in visitados:
                continue
            visitados.add((f, c))

            celda_actual = self.matriz[f][c]
            if celda_actual.revelada or celda_actual.marcada:
                continue

            celda_actual.revelada = True
            self.celdas_reveladas += 1
            resultado['celdas_reveladas'].append((f, c))

            # Si no tiene minas adyacentes, expandir
            if celda_actual.minas_adyacentes == 0:
                direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                for df, dc in direcciones:
                    nf, nc = f + df, c + dc
                    if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                        if (nf, nc) not in visitados:
                            cola.encolar(nf, nc)

        # Verificar victoria
        self._verificar_victoria()
        resultado['victoria'] = self.victoria
        resultado['game_over'] = self.victoria

        return resultado

    def marcar_celda(self, fila: int, col: int) -> bool:
        """Marca o desmarca una celda como posible mina"""
        if self.juego_terminado:
            return False

        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            return False

        celda = self.matriz[fila][col]

        if celda.revelada:
            return False

        celda.marcada = not celda.marcada
        self.historial.apilar(fila, col, "marcar")
        return True

    def deshacer_movimiento(self) -> bool:
        """Deshace el último movimiento usando la PILA"""
        if self.historial.esta_vacia():
            return False

        fila, col, accion = self.historial.desapilar()
        celda = self.matriz[fila][col]

        if accion == "revelar" and celda.revelada:
            celda.revelada = False
            self.celdas_reveladas -= 1
        elif accion == "marcar":
            celda.marcada = not celda.marcada

        return True

    def _verificar_victoria(self):
        """Verifica si el jugador ha ganado"""
        celdas_sin_minas = self.filas * self.columnas - self.num_minas
        if self.celdas_reveladas == celdas_sin_minas:
            self.juego_terminado = True
            self.victoria = True

    def reiniciar_juego(self):
        """Reinicia el juego completamente"""
        self.juego_terminado = False
        self.victoria = False
        self.celdas_reveladas = 0

        # Limpiar historial
        while not self.historial.esta_vacia():
            self.historial.desapilar()

        # Reiniciar todas las celdas
        for i in range(self.filas):
            for j in range(self.columnas):
                celda = self.matriz[i][j]
                celda.tiene_mina = False
                celda.revelada = False
                celda.marcada = False
                celda.minas_adyacentes = 0

        # Colocar nuevas minas
        self._colocar_minas()
        self._calcular_numeros()

    def obtener_banderas_restantes(self) -> int:
        """Retorna cuántas banderas quedan por colocar"""
        banderas_colocadas = 0
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.matriz[i][j].marcada:
                    banderas_colocadas += 1
        return self.num_minas - banderas_colocadas

    def revelar_todo(self) -> List[Tuple[int, int]]:
        """Retorna las posiciones de todas las minas"""
        minas = []
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.matriz[i][j].tiene_mina:
                    minas.append((i, j))
        return minas

    def obtener_estado_celda(self, fila: int, col: int) -> dict:
        """Retorna el estado de una celda"""
        celda = self.matriz[fila][col]
        return {
            'revelada': celda.revelada,
            'marcada': celda.marcada,
            'tiene_mina': celda.tiene_mina,
            'minas_adyacentes': celda.minas_adyacentes
        }

    def mostrar_tablero(self, revelar_todo: bool = False):
        """Muestra el tablero en consola"""
        print("\n   ", end="")
        for j in range(self.columnas):
            print(f"{j:2}", end=" ")
        print()

        for i in range(self.filas):
            print(f"{i:2} ", end="")
            for j in range(self.columnas):
                celda = self.matriz[i][j]

                if revelar_todo:
                    if celda.tiene_mina:
                        print(" * ", end="")
                    else:
                        print(f" {celda.minas_adyacentes} ", end="")
                else:
                    if celda.marcada:
                        print(" F ", end="")
                    elif celda.revelada:
                        if celda.tiene_mina:
                            print(" X ", end="")
                        elif celda.minas_adyacentes == 0:
                            print(" . ", end="")
                        else:
                            print(f" {celda.minas_adyacentes} ", end="")
                    else:
                        print(" # ", end="")
            print()
        print()


# FUNCIÓN PRINCIPAL PARA PROBAR

def main():
    """Función principal de prueba"""
    print("=== BUSCAMINAS - Backend ===\n")

    # Crear juego (10x10 con 15 minas)
    juego = Buscaminas(10, 10, 15)

    print("Instrucciones:")
    print("- Revelar: R fila columna")
    print("- Marcar: M fila columna")
    print("- Deshacer: U")
    print("- Nuevo: N")
    print("- Salir: Q\n")

    while True:
        juego.mostrar_tablero()

        if juego.juego_terminado:
            if juego.victoria:
                print("\n¡FELICIDADES! Has ganado.")
            else:
                print("\n¡BOOM! Has perdido.")
                juego.mostrar_tablero(revelar_todo=True)

            respuesta = input("\n¿Jugar de nuevo? (S/N): ").strip().upper()
            if respuesta == 'S':
                juego.reiniciar_juego()
                continue
            else:
                break

        comando = input("Ingresa comando: ").strip().upper().split()

        if not comando:
            continue

        if comando[0] == 'Q':
            break
        elif comando[0] == 'N':
            juego.reiniciar_juego()
        elif comando[0] == 'U':
            if juego.deshacer_movimiento():
                print("Movimiento deshecho")
            else:
                print("No hay movimientos para deshacer")
        elif comando[0] == 'R' and len(comando) == 3:
            try:
                fila = int(comando[1])
                col = int(comando[2])
                resultado = juego.revelar_celda(fila, col)
                if not resultado['valido']:
                    print("Movimiento inválido")
                elif resultado['game_over'] and not resultado['victoria']:
                    print("\n¡BOOM! Has perdido.")
            except ValueError:
                print("Coordenadas inválidas")
        elif comando[0] == 'M' and len(comando) == 3:
            try:
                fila = int(comando[1])
                col = int(comando[2])
                if juego.marcar_celda(fila, col):
                    print("Celda marcada/desmarcada")
                else:
                    print("No se puede marcar esta celda")
            except ValueError:
                print("Coordenadas inválidas")
        else:
            print("Comando inválido")

    print("\nGracias por jugar.")


if __name__ == "__main__":
    main()