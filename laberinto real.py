import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import math
import time

class AStarMazeSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Maze Solver 5x5 - Selección Gráfica")
        
        # Variables para el laberinto
        self.maze_size = 5
        self.maze = [[0 for _ in range(self.maze_size)] for _ in range(self.maze_size)]
        self.start_pos = None
        self.end_pos = None
        self.obstacles = 0
        self.setup_phase = "start"  # "start", "end", "obstacles", "ready"
        
        # Crear la interfaz gráfica
        self.create_widgets()
        
    def create_widgets(self):
        # Frame para el laberinto
        self.maze_frame = tk.Frame(self.root)
        self.maze_frame.pack(pady=10)
        
        # Crear celdas del laberinto con bindings de clic
        self.cells = []
        for i in range(self.maze_size):
            row = []
            for j in range(self.maze_size):
                cell = tk.Label(self.maze_frame, text="", width=4, height=2, 
                               relief="ridge", bg="white")
                cell.grid(row=i, column=j, padx=1, pady=1)
                cell.bind("<Button-1>", lambda e, i=i, j=j: self.cell_click(i, j))
                row.append(cell)
            self.cells.append(row)
        
        # Frame para los botones
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        # Botones
        self.setup_button = tk.Button(self.button_frame, text="Configurar Laberinto", 
                                    command=self.start_setup)
        self.setup_button.pack(side="left", padx=5)
        
        self.solve_button = tk.Button(self.button_frame, text="Resolver", 
                                     command=self.solve_maze)
        self.solve_button.pack(side="left", padx=5)
        
        self.clear_button = tk.Button(self.button_frame, text="Limpiar", 
                                     command=self.clear_maze)
        self.clear_button.pack(side="left", padx=5)
        
        # Etiqueta de instrucciones
        self.instructions = tk.Label(self.root, text="Haz clic en 'Configurar Laberinto' para comenzar", 
                                    fg="blue")
        self.instructions.pack(pady=5)
    
    def start_setup(self):
        self.clear_maze()
        self.setup_phase = "start"
        self.instructions.config(text="Selecciona la posición INICIAL (clic en una celda)")
    
    def cell_click(self, i, j):
        if self.setup_phase == "start":
            self.start_pos = (i, j)
            self.cells[i][j].config(text="I", bg="green")
            self.setup_phase = "end"
            self.instructions.config(text="Ahora selecciona la posición FINAL (clic en una celda)")
        elif self.setup_phase == "end":
            if (i, j) == self.start_pos:
                messagebox.showerror("Error", "El destino no puede ser igual al inicio")
                return
            self.end_pos = (i, j)
            self.cells[i][j].config(text="F", bg="red")
            self.setup_phase = "obstacles"
            self.ask_obstacles()
        elif self.setup_phase == "obstacles":
            # No hacemos nada aquí, los obstáculos se colocan aleatoriamente
            pass
    
    def ask_obstacles(self):
        try:
            max_obstacles = self.maze_size**2 - 2  # Máximo de obstáculos posibles
            self.obstacles = simpledialog.askinteger(
                "Obstáculos", 
                f"Ingrese cantidad de obstáculos (0-{max_obstacles}):", 
                parent=self.root,
                minvalue=0, 
                maxvalue=max_obstacles
            )
            
            if self.obstacles is None:  # Si el usuario cancela
                self.clear_maze()
                return
            
            # Colocar obstáculos aleatorios
            available_positions = [
                (i, j) for i in range(self.maze_size) for j in range(self.maze_size)
                if (i, j) != self.start_pos and (i, j) != self.end_pos
            ]
            
            for _ in range(self.obstacles):
                if not available_positions:
                    break
                pos = random.choice(available_positions)
                self.maze[pos[0]][pos[1]] = 1
                self.cells[pos[0]][pos[1]].config(bg="black")
                available_positions.remove(pos)
            
            self.setup_phase = "ready"
            self.instructions.config(text="Laberinto configurado. Haz clic en 'Resolver' para encontrar el camino")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al configurar obstáculos: {str(e)}")
            self.clear_maze()
    
    def clear_maze(self):
        self.maze = [[0 for _ in range(self.maze_size)] for _ in range(self.maze_size)]
        self.start_pos = None
        self.end_pos = None
        self.obstacles = 0
        self.setup_phase = "start"
        
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                self.cells[i][j].config(text="", bg="white")
        
        self.instructions.config(text="Haz clic en 'Configurar Laberinto' para comenzar")
    
    def solve_maze(self):
        if self.setup_phase != "ready":
            messagebox.showerror("Error", "Primero configura el laberinto completamente")
            return
        
        # Implementación del algoritmo A*
        class Node:
            def __init__(self, parent=None, position=None):
                self.parent = parent
                self.position = position
                self.g = 0  # Costo desde el inicio
                self.h = 0  # Heurística (distancia al destino)
                self.f = 0  # Costo total (g + h)
            
            def __eq__(self, other):
                return self.position == other.position
            
            def __hash__(self):
                return hash(self.position)
        
        # Crear nodos inicial y final
        start_node = Node(None, self.start_pos)
        end_node = Node(None, self.end_pos)
        
        # Inicializar listas abierta y cerrada
        open_list = []
        closed_list = set()
        
        # Añadir el nodo inicial
        open_list.append(start_node)
        
        # Movimientos posibles (arriba, abajo, izquierda, derecha, diagonales)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                 (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        found = False
        
        while open_list:
            # Obtener el nodo con menor costo f
            current_node = min(open_list, key=lambda x: x.f)
            open_list.remove(current_node)
            closed_list.add(current_node)
            
            # Dibujar el nodo actual (solo para visualización)
            i, j = current_node.position
            if current_node.position != self.start_pos and current_node.position != self.end_pos:
                self.cells[i][j].config(bg="yellow")
            self.root.update()
            time.sleep(0.1)  # Pequeña pausa para visualización
            
            # Si llegamos al destino
            if current_node.position == end_node.position:
                found = True
                break
            
            # Generar hijos
            children = []
            for move in moves:
                node_position = (current_node.position[0] + move[0], 
                                current_node.position[1] + move[1])
                
                # Verificar si está dentro del laberinto
                if (node_position[0] >= self.maze_size or node_position[0] < 0 or 
                    node_position[1] >= self.maze_size or node_position[1] < 0):
                    continue
                
                # Verificar si es un obstáculo
                if self.maze[node_position[0]][node_position[1]] == 1:
                    continue
                
                # Crear nuevo nodo
                new_node = Node(current_node, node_position)
                children.append(new_node)
            
            # Procesar hijos
            for child in children:
                # Si el hijo ya está en la lista cerrada
                if child in closed_list:
                    continue
                
                # Calcular g, h y f
                # Costo 1 para movimientos ortogonales, sqrt(2) para diagonales
                move_cost = 1.0 if abs(child.position[0] - current_node.position[0]) + \
                            abs(child.position[1] - current_node.position[1]) == 1 else math.sqrt(2)
                
                child.g = current_node.g + move_cost
                child.h = math.sqrt((child.position[0] - end_node.position[0])**2 + 
                            (child.position[1] - end_node.position[1])**2)  # Distancia euclidiana
                child.f = child.g + child.h
                
                # Si el hijo ya está en la lista abierta con un g menor
                existing_node = next((n for n in open_list if n == child), None)
                if existing_node and child.g >= existing_node.g:
                    continue
                
                # Añadir el hijo a la lista abierta
                open_list.append(child)
        
        if found:
            # Reconstruir el camino
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            
            # Mostrar el camino
            for pos in path[1:-1]:  # Excluir inicio y fin
                i, j = pos
                self.cells[i][j].config(bg="blue")
                self.root.update()
                time.sleep(0.1)
            
            messagebox.showinfo("Éxito", "¡Camino encontrado!")
        else:
            messagebox.showinfo("Error", "No se encontró un camino!")
    
    def run(self):
        self.root.mainloop()

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = AStarMazeSolver(root)
    app.run()