"""
Estructura de Datos - Entrega Final
David López y Jhon Alexis
Interfaz Gráfica (GUI)

IMPORTANTE: Este archivo debe estar en la misma carpeta que buscaminas_backend.py
"""

import tkinter as tk
from tkinter import messagebox

# Importar el backend
from Buscaminas import Buscaminas


class BuscaminasGUI:
    """Interfaz gráfica simple del juego Buscaminas"""

    def __init__(self, root):
        self.root = root
        self.root.title("Buscaminas - David López & Jhon Alexis")
        self.root.resizable(False, False)

        # Colores para los números
        self.colores = {
            1: 'blue',
            2: 'green',
            3: 'red',
            4: 'darkblue',
            5: 'darkred',
            6: 'cyan',
            7: 'black',
            8: 'gray'
        }

        # Configuración del juego
        self.filas = 10
        self.columnas = 10
        self.minas = 15
        self.juego = None
        self.botones = []

        # Crear interfaz
        self._crear_interfaz()
        self._nuevo_juego()

    def _crear_interfaz(self):
        """Crea los elementos visuales"""

        # Frame superior con controles
        frame_top = tk.Frame(self.root, bg='#34495e', padx=10, pady=10)
        frame_top.pack(fill=tk.X)

        # Contador de banderas
        self.label_banderas = tk.Label(
            frame_top,
            text="🚩 15",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='white'
        )
        self.label_banderas.pack(side=tk.LEFT, padx=20)

        # Botón Nuevo Juego
        tk.Button(
            frame_top,
            text="🔄 Nuevo",
            font=('Arial', 12, 'bold'),
            command=self._nuevo_juego,
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Botón Deshacer
        tk.Button(
            frame_top,
            text="↶ Deshacer",
            font=('Arial', 12, 'bold'),
            command=self._deshacer,
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Frame del tablero
        self.frame_tablero = tk.Frame(self.root, bg='#2c3e50', padx=10, pady=10)
        self.frame_tablero.pack()

        # Frame inferior con instrucciones
        frame_bottom = tk.Frame(self.root, bg='#34495e', padx=10, pady=8)
        frame_bottom.pack(fill=tk.X)

        tk.Label(
            frame_bottom,
            text="Click izquierdo: Revelar  |  Click derecho: Marcar",
            font=('Arial', 10),
            bg='#34495e',
            fg='white'
        ).pack()

    def _crear_tablero(self):
        """Crea el tablero de botones"""
        # Limpiar tablero anterior
        for widget in self.frame_tablero.winfo_children():
            widget.destroy()
        self.botones = []

        # Crear botones
        for i in range(self.filas):
            fila = []
            for j in range(self.columnas):
                btn = tk.Button(
                    self.frame_tablero,
                    text='',
                    width=3,
                    height=1,
                    font=('Arial', 12, 'bold'),
                    bg='#95a5a6',
                    relief=tk.RAISED,
                    borderwidth=2
                )
                btn.grid(row=i, column=j, padx=1, pady=1)

                # Eventos
                btn.bind('<Button-1>', lambda e, f=i, c=j: self._click_izquierdo(f, c))
                btn.bind('<Button-3>', lambda e, f=i, c=j: self._click_derecho(f, c))

                fila.append(btn)
            self.botones.append(fila)

    def _nuevo_juego(self):
        """Inicia un nuevo juego"""
        self.juego = Buscaminas(self.filas, self.columnas, self.minas)
        self._crear_tablero()
        self._actualizar_banderas()

    def _click_izquierdo(self, fila, col):
        """Maneja click izquierdo - Revelar"""
        resultado = self.juego.revelar_celda(fila, col)

        if not resultado['valido']:
            return

        # Actualizar celdas reveladas
        for f, c in resultado['celdas_reveladas']:
            self._actualizar_celda(f, c)

        # Verificar fin de juego
        if resultado['game_over']:
            if resultado['victoria']:
                self._victoria()
            else:
                self._derrota()

    def _click_derecho(self, fila, col):
        """Maneja click derecho - Marcar"""
        if self.juego.marcar_celda(fila, col):
            estado = self.juego.obtener_estado_celda(fila, col)
            btn = self.botones[fila][col]

            if estado['marcada']:
                btn.config(text='🚩', fg='red', font=('Arial', 10))
            else:
                btn.config(text='', fg='black')

            self._actualizar_banderas()

        return "break"

    def _actualizar_celda(self, fila, col):
        """Actualiza una celda revelada"""
        estado = self.juego.obtener_estado_celda(fila, col)
        btn = self.botones[fila][col]

        if estado['revelada']:
            btn.config(relief=tk.SUNKEN, bg='white', state=tk.DISABLED)

            if estado['tiene_mina']:
                btn.config(text='💣', bg='#e74c3c', font=('Arial', 10))
            elif estado['minas_adyacentes'] == 0:
                btn.config(text='')
            else:
                num = estado['minas_adyacentes']
                btn.config(text=str(num), fg=self.colores[num])

    def _actualizar_banderas(self):
        """Actualiza el contador de banderas"""
        restantes = self.juego.obtener_banderas_restantes()
        self.label_banderas.config(text=f"🚩 {restantes}")

    def _deshacer(self):
        """Deshace el último movimiento"""
        if self.juego.deshacer_movimiento():
            # Refrescar tablero
            for i in range(self.filas):
                for j in range(self.columnas):
                    estado = self.juego.obtener_estado_celda(i, j)
                    btn = self.botones[i][j]

                    if not estado['revelada']:
                        btn.config(
                            text='🚩' if estado['marcada'] else '',
                            fg='red' if estado['marcada'] else 'black',
                            bg='#95a5a6',
                            relief=tk.RAISED,
                            state=tk.NORMAL,
                            font=('Arial', 10 if estado['marcada'] else 12)
                        )
                    else:
                        self._actualizar_celda(i, j)

            self._actualizar_banderas()
        else:
            messagebox.showinfo("Deshacer", "No hay movimientos para deshacer")

    def _derrota(self):
        """Muestra derrota"""
        # Mostrar todas las minas
        minas = self.juego.revelar_todo()
        for f, c in minas:
            btn = self.botones[f][c]
            btn.config(text='💣', bg='#e74c3c', relief=tk.SUNKEN, font=('Arial', 10))

        messagebox.showinfo("Perdiste", "💥 ¡BOOM! Has perdido\n\n¡Inténtalo de nuevo!")

    def _victoria(self):
        """Muestra victoria"""
        messagebox.showinfo("¡Victoria!", "🎉 ¡Felicidades!\n\n¡Has ganado el juego!")


def main():
    """Función principal"""
    root = tk.Tk()
    app = BuscaminasGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()