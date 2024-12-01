import math
import tkinter as tk
from tkinter import simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import json


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")
        self.graph = nx.DiGraph()
        self.node_positions = {}
        self.selected_node = None

        # Canvas для графа
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Панель управления
        self.controls = tk.Frame(root, width=200, bg="lightgrey")
        self.controls.pack(side=tk.RIGHT, fill=tk.Y)

        self.add_controls()
        self.bind_events()

    def add_controls(self):
        """Добавить элементы управления в боковую панель."""
        tk.Label(self.controls, text="Graph Controls", bg="lightgrey", font=("Arial", 14)).pack(pady=10)

        # Кнопка добавления вершины
        tk.Button(self.controls, text="Add Node", command=self.add_node).pack(pady=5)

        # Кнопка удаления вершины
        tk.Button(self.controls, text="Remove Node", command=self.remove_node).pack(pady=5)

        # Кнопка добавления ребра
        tk.Button(self.controls, text="Add Edge", command=self.add_edge).pack(pady=5)

        # Кнопка удаления ребра
        tk.Button(self.controls, text="Remove Edge", command=self.remove_edge).pack(pady=5)

        # Кнопка BFS
        tk.Button(self.controls, text="Run BFS", command=self.run_bfs).pack(pady=5)

        # Кнопка DFS
        tk.Button(self.controls, text="Run DFS", command=self.run_dfs).pack(pady=5)

        # Кнопка загрузки графа из JSON
        tk.Button(self.controls, text="Load JSON", command=self.load_graph_from_json_prompt).pack(pady=5)

    def bind_events(self):
        """Связываем события с Canvas."""
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_left_click(self, event):
        """Обрабатываем клик левой кнопкой мыши."""
        for node, pos in self.node_positions.items():
            if (event.x - pos[0]) ** 2 + (event.y - pos[1]) ** 2 < 400:
                self.selected_node = node
                return
        # Если не попали в узел, создаём новый
        self.add_node(event.x, event.y)

    def on_drag(self, event):
        """Перетаскиваем вершину."""
        if self.selected_node:
            self.node_positions[self.selected_node] = (event.x, event.y)
            self.redraw_canvas()

    def on_release(self, event):
        """Сбрасываем выбор вершины."""
        self.selected_node = None

    def add_node(self, x=None, y=None):
        """Добавить вершину в граф."""
        node_id = len(self.graph) + 1
        self.graph.add_node(node_id)
        if x is None or y is None:  # Если координаты не указаны, создаём случайные
            x, y = 100, 100
        self.node_positions[node_id] = (x, y)
        self.redraw_canvas()

    def remove_node(self):
        """Удалить вершину."""
        node_id = simpledialog.askinteger("Remove Node", "Enter node ID to remove:")
        if node_id and node_id in self.graph:
            self.graph.remove_node(node_id)
            del self.node_positions[node_id]
            self.redraw_canvas()

    def add_edge(self):
        """Добавить ребро."""
        source = simpledialog.askinteger("Add Edge", "Enter source node ID:")
        target = simpledialog.askinteger("Add Edge", "Enter target node ID:")
        weight = simpledialog.askfloat("Add Edge", "Enter edge weight:", initialvalue=1.0)
        if source and target and weight:
            if source in self.graph.nodes and target in self.graph.nodes:
                self.graph.add_edge(source, target, weight=weight)
                self.redraw_canvas()
            else:
                print(f"Error: One or both nodes ({source}, {target}) do not exist.")

    def remove_edge(self):
        """Удалить ребро."""
        source = simpledialog.askinteger("Remove Edge", "Enter source node ID:")
        target = simpledialog.askinteger("Remove Edge", "Enter target node ID:")
        if source and target and self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
            self.redraw_canvas()

    import math

    def redraw_canvas(self):
        """Обновить Canvas с текущим графом."""
        self.canvas.delete("all")
        radius = 10  # Радиус узла для корректировки окончания стрелок

        # Рисуем рёбра
        for u, v in self.graph.edges:
            if u in self.node_positions and v in self.node_positions:
                x1, y1 = self.node_positions[u]
                x2, y2 = self.node_positions[v]

                # Рассчитываем угол для корректировки окончания стрелки
                angle = math.atan2(y2 - y1, x2 - x1)
                x2_adjusted = x2 - radius * math.cos(angle)
                y2_adjusted = y2 - radius * math.sin(angle)

                # Рисуем стрелку для направленного ребра
                self.canvas.create_line(x1, y1, x2_adjusted, y2_adjusted, arrow=tk.LAST, fill="black")

                # Вычисляем положение текста с весом
                edge_weight = self.graph[u][v].get("weight", 1.0)
                text_x = (x1 + x2) / 2
                text_y = (y1 + y2) / 2
                self.canvas.create_text(text_x, text_y, text=str(edge_weight), fill="red")

        # Рисуем вершины
        for node, (x, y) in self.node_positions.items():
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="blue")
            self.canvas.create_text(x, y, text=str(node))

        # Рисуем вершины
        for node, (x, y) in self.node_positions.items():
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="blue")
            self.canvas.create_text(x, y, text=str(node))


    def run_bfs(self):
        """Визуализация BFS."""
        start_node = simpledialog.askinteger("BFS", "Enter start node ID:")
        if not start_node or start_node not in self.graph:
            return
        visited = set()
        queue = [start_node]

        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                self.highlight_node(current, "green")
                time.sleep(0.5)
                self.root.update()
                for neighbor in self.graph.neighbors(current):
                    if neighbor not in visited:
                        queue.append(neighbor)

    def run_dfs(self):
        """Визуализация DFS."""
        start_node = simpledialog.askinteger("DFS", "Enter start node ID:")
        if not start_node or start_node not in self.graph:
            return

        visited = set()

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            self.highlight_node(node, "orange")
            time.sleep(0.5)
            self.root.update()
            for neighbor in self.graph.neighbors(node):
                dfs(neighbor)

        dfs(start_node)

    def highlight_node(self, node, color):
        """Подсветка узла."""
        x, y = self.node_positions[node]
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=color)
        self.canvas.create_text(x, y, text=str(node))

    def load_graph_from_json(self, json_file):
        """Загрузить граф из JSON-файла с преобразованием вершин в числа и установкой весов по умолчанию."""
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

            if not data.get("adj_list"):
                print("Invalid JSON: 'adj_list' key not found.")
                return

            self.graph.clear()
            self.node_positions.clear()

            node_mapping = {}
            current_id = 1  # Начинаем нумерацию с 1

            # Преобразуем вершины в числа
            for node in data["adj_list"]:
                node_mapping[node] = current_id
                self.graph.add_node(current_id)
                self.node_positions[current_id] = (100 + len(self.node_positions) * 50, 100)
                current_id += 1

            # Добавляем рёбра с весами
            for node, edges in data["adj_list"].items():
                for edge in edges:
                    source = node_mapping[node]
                    target = node_mapping[edge["to"]]
                    self.graph.add_edge(source, target, weight=1.0)  # Устанавливаем вес по умолчанию

            self.redraw_canvas()
            print(f"Graph loaded from {json_file} with numeric nodes and default weights.")
        except Exception as e:
            print(f"Error loading JSON: {e}")

    def load_graph_from_json_prompt(self):
        """Открыть диалог для выбора JSON-файла и загрузить граф."""
        json_file = simpledialog.askstring("Load JSON", "Enter path to JSON file:")
        if json_file:
            self.load_graph_from_json(json_file)


# Запуск приложения
root = tk.Tk()
app = GraphApp(root)
root.mainloop()