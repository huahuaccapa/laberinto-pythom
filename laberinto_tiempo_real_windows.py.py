import numpy as np
import heapq
import random
import tkinter as tk
from collections import deque
from tkinter import messagebox, simpledialog
import time

# Configuración inicial
ANCHO = 15
ALTO = 10
MAX_BLOQUES = ANCHO * ALTO // 2  # Máximo razonable de bloques
VELOCIDAD_IA = 0.5

COLORES = {
    'jugador': '#2ecc71',   # Verde
    'ruta_jugador': '#27ae60', # Verde oscuro
    'ia': '#e74c3c',        # Rojo
    'ruta_ia': '#9b59b6',   # Morado
    'objetivo': '#f39c12',  # Amarillo
    'pared': '#34495e',     # Gris oscuro
    'camino': '#ecf0f1',    # Blanco grisáceo
    'texto': '#2c3e50',     # Azul oscuro
    'fondo': '#ffffff'      # Blanco
}

class Laberinto:
    def __init__(self, num_bloques=0):
        self.num_bloques = num_bloques
        self.grid = np.zeros((ALTO, ANCHO), dtype=int)
        self.reset_posiciones()
        self.generar_laberinto_valido()
    
    def generar_posicion_aleatoria_valida(self, excluir=[]):
        """Genera una posición aleatoria que no sea pared y sea accesible"""
        while True:
            pos = (random.randint(0, ALTO-1), random.randint(0, ANCHO-1))
            if pos not in excluir and self.grid[pos] == 0:
                return pos
    
    def reset_posiciones(self):
        """Reinicia las posiciones sin cambiar el laberinto"""
        self.jugador = (0, 0)
        self.ia = (ALTO-1, 0)
        # El objetivo ahora se coloca aleatoriamente en cada nueva partida
        self.objetivo = self.generar_posicion_aleatoria_valida(excluir=[self.jugador, self.ia])
        self.ruta_ia = []
        self.ruta_jugador = []
    
    def hay_camino(self, inicio, fin):
        """BFS para verificar conectividad"""
        visitados = set()
        cola = deque([inicio])
        visitados.add(inicio)
        
        while cola:
            x, y = cola.popleft()
            
            if (x, y) == fin:
                return True
            
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < ALTO and 0 <= ny < ANCHO and 
                    self.grid[nx][ny] == 0 and (nx, ny) not in visitados):
                    visitados.add((nx, ny))
                    cola.append((nx, ny))
        
        return False
    
    def generar_laberinto_valido(self):
        """Genera un laberinto con exactamente num_bloques paredes y objetivo accesible"""
        intentos = 0
        while intentos < 100:  # Límite de intentos para evitar bucles infinitos
            self.grid = np.zeros((ALTO, ANCHO), dtype=int)
            
            # Generar bloques exactos
            posiciones_disponibles = [
                (i, j) for i in range(ALTO) for j in range(ANCHO)
                if (i, j) not in [self.jugador, self.ia]
            ]
            
            # Seleccionar posiciones aleatorias para los bloques
            bloques_colocados = 0
            random.shuffle(posiciones_disponibles)
            
            for i, j in posiciones_disponibles:
                if bloques_colocados < self.num_bloques:
                    self.grid[i][j] = 1
                    bloques_colocados += 1
            
            # Colocar objetivo en posición aleatoria accesible
            self.objetivo = self.generar_posicion_aleatoria_valida(excluir=[self.jugador, self.ia])
            
            # Verificar caminos válidos
            if (self.hay_camino(self.jugador, self.objetivo) and 
                self.hay_camino(self.ia, self.objetivo)):
                # Calcular rutas iniciales
                self.ruta_ia = astar(self.grid, self.ia, self.objetivo)
                self.ruta_jugador = astar(self.grid, self.jugador, self.objetivo)
                return
            
            intentos += 1
        
        # Si no se encontró un laberinto válido después de muchos intentos
        self.num_bloques = max(0, self.num_bloques - 1)
        self.generar_laberinto_valido()

class Nodo:
    def __init__(self, posicion, padre=None):
        self.posicion = posicion
        self.padre = padre
        self.g = 0  # Costo desde inicio
        self.h = 0  # Heurística hasta objetivo
        self.f = 0  # Costo total
    
    def __eq__(self, otro):
        return self.posicion == otro.posicion
    
    def __lt__(self, otro):
        return self.f < otro.f

def astar(laberinto, inicio, objetivo):
    """Algoritmo A* para encontrar el camino más corto"""
    lista_abierta = []
    lista_cerrada = set()
    
    heapq.heappush(lista_abierta, Nodo(inicio))
    
    while lista_abierta:
        nodo_actual = heapq.heappop(lista_abierta)
        lista_cerrada.add(nodo_actual.posicion)
        
        if nodo_actual.posicion == objetivo:
            camino = []
            while nodo_actual:
                camino.append(nodo_actual.posicion)
                nodo_actual = nodo_actual.padre
            return camino[::-1]
        
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nueva_pos = (nodo_actual.posicion[0] + dx, nodo_actual.posicion[1] + dy)
            
            if (0 <= nueva_pos[0] < ALTO and 0 <= nueva_pos[1] < ANCHO and 
                laberinto[nueva_pos] == 0 and nueva_pos not in lista_cerrada):
                
                nuevo_nodo = Nodo(nueva_pos, nodo_actual)
                nuevo_nodo.g = nodo_actual.g + 1
                nuevo_nodo.h = abs(nueva_pos[0] - objetivo[0]) + abs(nueva_pos[1] - objetivo[1])
                nuevo_nodo.f = nuevo_nodo.g + nuevo_nodo.h
                
                heapq.heappush(lista_abierta, nuevo_nodo)
    
    return []

class JuegoLaberinto:
    def __init__(self, master):
        self.master = master
        self.master.title("Laberinto con Rutas Visibles")
        self.master.configure(bg=COLORES['fondo'])
        
        # Estadísticas
        self.victorias_jugador = 0
        self.victorias_ia = 0
        self.num_bloques_actual = 10  # Valor inicial de bloques
        self.juego_activo = False  # Estado de espera para comenzar
        
        # Interfaz
        self.crear_interfaz()
        
        # Iniciar juego
        self.nuevo_juego()
        self.ultimo_movimiento_ia = time.time()
        self.actualizar_ia()
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        # Frame superior
        self.frame_superior = tk.Frame(self.master, bg=COLORES['fondo'])
        self.frame_superior.pack(pady=5, fill=tk.X)
        
        # Marcador
        self.lbl_marcador = tk.Label(
            self.frame_superior, 
            text=f"Victorias - Tú: {self.victorias_jugador} | IA: {self.victorias_ia} | Bloques: {self.num_bloques_actual}",
            font=('Helvetica', 12, 'bold'), 
            fg=COLORES['texto'],
            bg=COLORES['fondo']
        )
        self.lbl_marcador.pack(side=tk.LEFT, padx=10)
        
        # Botón de configuración
        self.btn_config = tk.Button(
            self.frame_superior,
            text="Configurar Bloques",
            command=self.configurar_bloques,
            bg=COLORES['camino'],
            fg=COLORES['texto'],
            relief=tk.RAISED
        )
        self.btn_config.pack(side=tk.RIGHT, padx=10)
        
        # Canvas para el laberinto
        self.canvas = tk.Canvas(
            self.master, 
            width=ANCHO*40, 
            height=ALTO*40, 
            bg=COLORES['camino'], 
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Controles
        self.lbl_controles = tk.Label(
            self.master, 
            text="Controles: WASD (movimiento) | Q (salir) | Presiona Enter para comenzar",
            font=('Helvetica', 10), 
            fg=COLORES['texto'],
            bg=COLORES['fondo']
        )
        self.lbl_controles.pack(pady=5)
        
        # Bind de teclado
        self.master.bind("<Key>", self.manejar_teclado)
    
    def configurar_bloques(self):
        """Permite configurar el número exacto de bloques"""
        try:
            nuevo_num = simpledialog.askinteger(
                "Configurar Bloques",
                f"Ingrese número de bloques (0-{MAX_BLOQUES}):",
                parent=self.master,
                minvalue=0,
                maxvalue=MAX_BLOQUES,
                initialvalue=self.num_bloques_actual
            )
            
            if nuevo_num is not None:
                self.num_bloques_actual = nuevo_num
                self.actualizar_marcador()
                self.nuevo_juego()
                self.mostrar_mensaje_inicio()
        except:
            messagebox.showerror("Error", f"Por favor ingrese un número entre 0 y {MAX_BLOQUES}")
    
    def mostrar_mensaje_inicio(self):
        """Muestra mensaje de inicio"""
        self.juego_activo = False
        self.canvas.create_text(
            ANCHO*20, ALTO*20,
            text="Presiona Enter para comenzar",
            font=('Helvetica', 16, 'bold'),
            fill=COLORES['texto'],
            tags="mensaje"
        )
    
    def nuevo_juego(self):
        """Inicia un nuevo juego con la configuración actual"""
        self.laberinto = Laberinto(self.num_bloques_actual)
        self.dibujar_laberinto()
    
    def dibujar_laberinto(self):
        """Dibuja el laberinto completo con rutas (ahora con líneas)"""
        self.canvas.delete("all")
        
        # Dibujar paredes/bloques
        for i in range(ALTO):
            for j in range(ANCHO):
                if self.laberinto.grid[i][j] == 1:
                    self.canvas.create_rectangle(
                        j*40, i*40, j*40+40, i*40+40,
                        fill=COLORES['pared'], outline=COLORES['pared']
                    )
        
        # Dibujar ruta del jugador (líneas verdes)
        if len(self.laberinto.ruta_jugador) > 1:
            puntos_jugador = [(y*40+20, x*40+20) for x, y in self.laberinto.ruta_jugador]
            self.canvas.create_line(
                puntos_jugador,
                fill=COLORES['ruta_jugador'],
                width=3,
                smooth=True
            )
        
        # Dibujar ruta de la IA (líneas moradas)
        if len(self.laberinto.ruta_ia) > 1:
            puntos_ia = [(y*40+20, x*40+20) for x, y in self.laberinto.ruta_ia]
            self.canvas.create_line(
                puntos_ia,
                fill=COLORES['ruta_ia'],
                width=3,
                smooth=True
            )
        
        # Dibujar objetivo
        obj_x, obj_y = self.laberinto.objetivo
        self.canvas.create_oval(
            obj_y*40+5, obj_x*40+5, obj_y*40+35, obj_x*40+35,
            fill=COLORES['objetivo'], outline=COLORES['objetivo']
        )
        
        # Dibujar jugador
        j_x, j_y = self.laberinto.jugador
        self.canvas.create_oval(
            j_y*40+5, j_x*40+5, j_y*40+35, j_x*40+35,
            fill=COLORES['jugador'], outline=COLORES['jugador']
        )
        
        # Dibujar IA
        ia_x, ia_y = self.laberinto.ia
        self.canvas.create_oval(
            ia_y*40+5, ia_x*40+5, ia_y*40+35, ia_x*40+35,
            fill=COLORES['ia'], outline=COLORES['ia']
        )
    
    def manejar_teclado(self, event):
        """Gestiona las entradas de teclado"""
        if not self.juego_activo:
            if event.keysym == 'Return':
                self.juego_activo = True
                self.canvas.delete("mensaje")
            return
        
        key = event.keysym.lower()
        
        if key in ['w', 'a', 's', 'd']:
            self.mover_jugador(key)
        elif key == 'q':
            self.master.quit()
    
    def mover_jugador(self, direccion):
        """Mueve al jugador y actualiza su ruta"""
        if not self.juego_activo:
            return
            
        dx, dy = 0, 0
        
        if direccion == 'w' and self.laberinto.jugador[0] > 0:
            dx = -1
        elif direccion == 's' and self.laberinto.jugador[0] < ALTO-1:
            dx = 1
        elif direccion == 'a' and self.laberinto.jugador[1] > 0:
            dy = -1
        elif direccion == 'd' and self.laberinto.jugador[1] < ANCHO-1:
            dy = 1
        
        nueva_pos = (self.laberinto.jugador[0]+dx, self.laberinto.jugador[1]+dy)
        
        if (0 <= nueva_pos[0] < ALTO and 0 <= nueva_pos[1] < ANCHO and 
            self.laberinto.grid[nueva_pos] == 0):
            self.laberinto.jugador = nueva_pos
            # Recalcular ruta del jugador
            self.laberinto.ruta_jugador = astar(self.laberinto.grid, self.laberinto.jugador, self.laberinto.objetivo)
            self.dibujar_laberinto()
            self.verificar_fin_juego()
    
    def actualizar_ia(self):
        """Actualiza el movimiento de la IA"""
        if self.juego_activo and time.time() - self.ultimo_movimiento_ia > VELOCIDAD_IA:
            # Recalcular ruta completa de la IA
            self.laberinto.ruta_ia = astar(self.laberinto.grid, self.laberinto.ia, self.laberinto.objetivo)
            
            if len(self.laberinto.ruta_ia) > 1:
                self.laberinto.ia = self.laberinto.ruta_ia[1]
                self.dibujar_laberinto()
                self.verificar_fin_juego()
            
            self.ultimo_movimiento_ia = time.time()
        
        self.master.after(100, self.actualizar_ia)
    
    def verificar_fin_juego(self):
        """Verifica si el juego ha terminado y reinicia automáticamente"""
        if not self.juego_activo:
            return
            
        if self.laberinto.jugador == self.laberinto.objetivo:
            self.victorias_jugador += 1
            self.actualizar_marcador()
            self.juego_activo = False
            messagebox.showinfo("¡Ganaste!", "¡Llegaste al objetivo primero! 😊")
            self.nuevo_juego()  # Reiniciar automáticamente
            self.mostrar_mensaje_inicio()
        elif self.laberinto.ia == self.laberinto.objetivo:
            self.victorias_ia += 1
            self.actualizar_marcador()
            self.juego_activo = False
            messagebox.showinfo("Perdiste", "La IA llegó primero al objetivo 🤖")
            self.nuevo_juego()  # Reiniciar automáticamente
            self.mostrar_mensaje_inicio()
        elif self.laberinto.jugador == self.laberinto.ia:
            self.victorias_ia += 1
            self.actualizar_marcador()
            self.juego_activo = False
            messagebox.showinfo("Perdiste", "¡La IA te atrapó! 💀")
            self.nuevo_juego()  # Reiniciar automáticamente
            self.mostrar_mensaje_inicio()
    
    def actualizar_marcador(self):
        """Actualiza el marcador en la interfaz"""
        self.lbl_marcador.config(
            text=f"Victorias - Tú: {self.victorias_jugador} | IA: {self.victorias_ia} | Bloques: {self.num_bloques_actual}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x600")
    root.resizable(False, False)
    
    try:
        juego = JuegoLaberinto(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
