import tkinter as tk
import math

class PolyhedronViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Проективные преобразования - Тетраэдр и Додекаэдр")
        self.root.geometry("800x700")

        # Параметры отображения
        self.rotation_x = 0
        self.rotation_y = 0
        self.center_x = 400
        self.center_y = 300
        self.scale = 120

        self.orthographic = True
        self.current_polyhedron = "Тетраэдр"  # По умолчанию показываем тетраэдр

        # Инициализация геометрии
        self.vertices = []
        self.edges = []
        self.faces = []

        self.create_polyhedra()
        self.create_widgets()
        self.draw_polyhedron()

        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Button-1>", self.on_mouse_click)

    def create_polyhedra(self):
        # ========== ТЕТРАЭДР ==========
        # Вершины тетраэдра (правильный тетраэдр)
        a = 1.0
        h = math.sqrt(2/3) * a  # высота тетраэдра

        self.tetrahedron_vertices = [
            (0, 0, h),                           # Верхняя вершина
            (0, 2*a/3, -h/3),                    # Нижняя вершина 1
            (a/math.sqrt(3), -a/3, -h/3),        # Нижняя вершина 2
            (-a/math.sqrt(3), -a/3, -h/3)        # Нижняя вершина 3
        ]

        # Рёбра тетраэдра
        self.tetrahedron_edges = [
            (0, 1), (0, 2), (0, 3),  # рёбра от верхней вершины
            (1, 2), (2, 3), (3, 1)   # рёбра основания
        ]

        # ========== ДОДЕКАЭДР ==========
        # Золотое сечение
        phi = (1 + math.sqrt(5)) / 2

        # Вершины додекаэдра (12 вершин)
        self.dodecahedron_vertices = []

        # Циклическая перестановка (±1, ±1, ±1)
        for i in range(8):
            x = 1 if (i & 1) else -1
            y = 1 if (i & 2) else -1
            z = 1 if (i & 4) else -1
            self.dodecahedron_vertices.append((x, y, z))

        # Циклическая перестановка (0, ±1/φ, ±φ)
        for i in range(4):
            sign1 = 1 if (i & 1) else -1
            sign2 = 1 if (i & 2) else -1

            self.dodecahedron_vertices.append((0, sign1/phi, sign2*phi))
            self.dodecahedron_vertices.append((sign1/phi, sign2*phi, 0))
            self.dodecahedron_vertices.append((sign2*phi, 0, sign1/phi))

        # Нормализуем вершины для лучшего отображения
        self.dodecahedron_vertices = [self.normalize_vertex(v, 1.5) for v in self.dodecahedron_vertices]

        # Рёбра додекаэдра (соединяем вершины, которые находятся на расстоянии ~2/φ)
        self.dodecahedron_edges = []
        edge_distance = 2/phi + 0.1

        for i in range(len(self.dodecahedron_vertices)):
            for j in range(i + 1, len(self.dodecahedron_vertices)):
                if self.distance(self.dodecahedron_vertices[i],
                                 self.dodecahedron_vertices[j]) < edge_distance:
                    self.dodecahedron_edges.append((i, j))

        # Устанавливаем начальный многогранник
        self.set_polyhedron("Тетраэдр")

    def normalize_vertex(self, vertex, factor=1.0):
        x, y, z = vertex
        length = math.sqrt(x*x + y*y + z*z)
        return (x/length * factor, y/length * factor, z/length * factor)

    def distance(self, v1, v2):
        x1, y1, z1 = v1
        x2, y2, z2 = v2
        return math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

    def set_polyhedron(self, name):
        self.current_polyhedron = name
        if name == "Тетраэдр":
            self.vertices = self.tetrahedron_vertices
            self.edges = self.tetrahedron_edges
        else:  # Додекаэдр
            self.vertices = self.dodecahedron_vertices
            self.edges = self.dodecahedron_edges

    def rotate_vertex(self, vertex, rx, ry):
        x, y, z = vertex

        # Вращение вокруг оси X
        y_rot = y * math.cos(rx) - z * math.sin(rx)
        z_rot = y * math.sin(rx) + z * math.cos(rx)
        y, z = y_rot, z_rot

        # Вращение вокруг оси Y
        x_rot = x * math.cos(ry) + z * math.sin(ry)
        z_rot = -x * math.sin(ry) + z * math.cos(ry)
        x, z = x_rot, z_rot

        return (x, y, z)

    def project_vertex(self, vertex):
        x, y, z = vertex

        if self.orthographic:
            # Ортогональная проекция
            x_proj = x
            y_proj = y
        else:
            # Центральная (перспективная) проекция
            distance = 5
            if distance - z != 0:
                factor = distance / (distance - z)
                x_proj = x * factor
                y_proj = y * factor
            else:
                x_proj = x
                y_proj = y

        # Преобразование в экранные координаты
        screen_x = self.center_x + x_proj * self.scale
        screen_y = self.center_y - y_proj * self.scale

        return (screen_x, screen_y, z)

    def create_widgets(self):
        # Панель управления
        control_frame = tk.Frame(self.root, bg="lightgray")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Выбор проекции
        projection_frame = tk.Frame(control_frame, bg="lightgray")
        projection_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(projection_frame, text="Проекция:", bg="lightgray").pack(side=tk.LEFT)

        self.projection_var = tk.BooleanVar(value=self.orthographic)
        tk.Radiobutton(projection_frame, text="Ортогональная",
                       variable=self.projection_var, value=True,
                       command=self.toggle_projection, bg="lightgray").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(projection_frame, text="Центральная",
                       variable=self.projection_var, value=False,
                       command=self.toggle_projection, bg="lightgray").pack(side=tk.LEFT, padx=5)

        # Выбор многогранника
        polyhedron_frame = tk.Frame(control_frame, bg="lightgray")
        polyhedron_frame.pack(side=tk.RIGHT, padx=10)

        tk.Label(polyhedron_frame, text="Многогранник:", bg="lightgray").pack(side=tk.LEFT)

        self.polyhedron_var = tk.StringVar(value=self.current_polyhedron)
        tk.Radiobutton(polyhedron_frame, text="Тетраэдр",
                       variable=self.polyhedron_var, value="Тетраэдр",
                       command=self.change_polyhedron, bg="lightgray").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(polyhedron_frame, text="Додекаэдр",
                       variable=self.polyhedron_var, value="Додекаэдр",
                       command=self.change_polyhedron, bg="lightgray").pack(side=tk.LEFT, padx=5)

        # Информационная панель
        info_frame = tk.Frame(self.root, bg="lightgray", height=30)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        info_frame.pack_propagate(False)

        self.info_label = tk.Label(info_frame, text="", bg="lightgray")
        self.info_label.pack(pady=5)

        # Холст для рисования
        self.canvas = tk.Canvas(self.root, width=800, height=550, bg="white")
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def toggle_projection(self):
        self.orthographic = self.projection_var.get()
        self.draw_polyhedron()

    def change_polyhedron(self):
        polyhedron_name = self.polyhedron_var.get()
        self.set_polyhedron(polyhedron_name)
        self.draw_polyhedron()

    def on_mouse_click(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def on_mouse_drag(self, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y

        self.rotation_y += dx * 0.01
        self.rotation_x += dy * 0.01

        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        self.draw_polyhedron()

    def draw_polyhedron(self):
        self.canvas.delete("all")

        # Вращение и проекция вершин
        rotated_vertices = []
        projected_vertices = []

        for vertex in self.vertices:
            rotated = self.rotate_vertex(vertex, self.rotation_x, self.rotation_y)
            projected = self.project_vertex(rotated)
            rotated_vertices.append(rotated)
            projected_vertices.append(projected)

        # Сортируем рёбра по глубине для правильного отображения (опционально)
        edges_with_depth = []
        for edge in self.edges:
            i, j = edge
            z1 = projected_vertices[i][2]
            z2 = projected_vertices[j][2]
            avg_depth = (z1 + z2) / 2
            edges_with_depth.append((avg_depth, edge))

        # Рисуем рёбра (сначала дальние)
        edges_with_depth.sort(reverse=True)  # дальние -> ближние

        for depth, edge in edges_with_depth:
            i, j = edge
            x1, y1, _ = projected_vertices[i]
            x2, y2, _ = projected_vertices[j]

            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        # Рисуем вершины
        for x, y, _ in projected_vertices:
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4,
                                    fill="red", outline="red")

        # Обновляем информацию
        proj_type = "Ортогональная" if self.orthographic else "Центральная"
        vertex_count = len(self.vertices)
        edge_count = len(self.edges)

        info_text = f"{self.current_polyhedron} | {proj_type} проекция | "
        info_text += f"Вершин: {vertex_count} | Рёбер: {edge_count} | "
        info_text += "Перетащите мышь для вращения"

        self.info_label.config(text=info_text)

def main():
    root = tk.Tk()
    app = PolyhedronViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()