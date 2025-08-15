from collections import deque
import math
import random
from PyQt5.QtCore import QPoint, QPointF
import json


class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = []
        # Thêm dictionary để lưu điểm điều khiển cho cạnh cong
        self.edge_control_points = {}

    def add_vertex(self, vertex):
        name, _ = vertex
        if name not in [v[0] for v in self.vertices]:
            self.vertices.append(vertex)

    def add_edge(self, edge):
        name1, name2 = edge
        if edge not in self.edges and (name2, name1) not in self.edges:
            self.edges.append(edge)
            # Tạo điểm điều khiển mặc định cho cạnh mới
            self.create_default_control_point(edge)

    def create_default_control_point(self, edge):
        """Tạo điểm điều khiển mặc định cho cạnh"""
        name1, name2 = edge
        pos1 = next((pos for n, pos in self.vertices if n == name1), None)
        pos2 = next((pos for n, pos in self.vertices if n == name2), None)
        
        if pos1 and pos2:
            # Điểm điều khiển ở giữa cạnh, lệch lên trên một chút
            mid_x = (pos1.x() + pos2.x()) / 2
            mid_y = (pos1.y() + pos2.y()) / 2 - 30
            control_point = QPointF(mid_x, mid_y)
            
            # Lưu cho cả hai hướng của cạnh
            self.edge_control_points[edge] = control_point
            self.edge_control_points[(name2, name1)] = control_point

    def get_control_point(self, edge):
        """Lấy điểm điều khiển của cạnh"""
        return self.edge_control_points.get(edge, None)

    def set_control_point(self, edge, point):
        """Đặt điểm điều khiển cho cạnh"""
        name1, name2 = edge
        self.edge_control_points[edge] = point
        self.edge_control_points[(name2, name1)] = point

    def remove_vertex(self, vertex):
        name, _ = vertex
        self.vertices = [v for v in self.vertices if v[0] != name]
        # Xóa các cạnh và điểm điều khiển liên quan
        edges_to_remove = [e for e in self.edges if name in e]
        for edge in edges_to_remove:
            self.edges.remove(edge)
            self.edge_control_points.pop(edge, None)
            # Xóa cả hướng ngược lại
            reverse_edge = (edge[1], edge[0])
            self.edge_control_points.pop(reverse_edge, None)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
            # Xóa điểm điều khiển
            self.edge_control_points.pop(edge, None)
            self.edge_control_points.pop((edge[1], edge[0]), None)

    def clear(self):
        self.vertices.clear()
        self.edges.clear()
        self.edge_control_points.clear()

def connected_components(graph):
    vertices = [v[0] for v in graph.vertices]
    adjacency = {v: set() for v in vertices}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    visited = set()
    components = []

    def dfs(u, component):
        visited.add(u)
        component.append(u)
        for v in adjacency[u]:
            if v not in visited:
                dfs(v, component)

    for v in vertices:
        if v not in visited:
            component = []
            dfs(v, component)
            components.append(sorted(component))  # Sắp xếp để dễ đọc

    return len(components), components


def generate_random_graph(graph, num_vertices=None, edge_probability=0.4, width=600, height=500):
    if num_vertices is None:
        num_vertices = random.randint(3, 6)
    graph.clear()
    spacing = 360 / num_vertices
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y) - 60

    for i in range(num_vertices):
        name = chr(65 + i)
        angle_rad = math.radians(i * spacing)
        x = center_x + int(radius * math.cos(angle_rad))
        y = center_y + int(radius * math.sin(angle_rad))
        graph.add_vertex((name, QPoint(x, y)))

    vertices = [v[0] for v in graph.vertices]
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if random.random() < edge_probability:
                graph.add_edge((vertices[i], vertices[j]))


def format_graph_circular(graph, width=600, height=500):
    """Sắp xếp đồ thị theo hình tròn"""
    if not graph.vertices:
        return
    
    num_vertices = len(graph.vertices)
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y) - 80
    
    for i, (name, _) in enumerate(graph.vertices):
        angle = 2 * math.pi * i / num_vertices
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        graph.vertices[i] = (name, QPoint(x, y))
    
    # Reset control points for all edges
    for edge in graph.edges:
        graph.create_default_control_point(edge)


def format_graph_grid(graph, width=600, height=500):
    """Sắp xếp đồ thị theo lưới"""
    if not graph.vertices:
        return
    
    num_vertices = len(graph.vertices)
    cols = math.ceil(math.sqrt(num_vertices))
    rows = math.ceil(num_vertices / cols)
    
    margin = 80
    cell_width = (width - 2 * margin) / cols
    cell_height = (height - 2 * margin) / rows
    
    for i, (name, _) in enumerate(graph.vertices):
        row = i // cols
        col = i % cols
        x = margin + col * cell_width + cell_width // 2
        y = margin + row * cell_height + cell_height // 2
        graph.vertices[i] = (name, QPoint(int(x), int(y)))
    
    # Reset control points for all edges
    for edge in graph.edges:
        graph.create_default_control_point(edge)


def format_graph_spring(graph, width=600, height=500, iterations=100):
    """Sắp xếp đồ thị bằng thuật toán spring (force-directed)"""
    if not graph.vertices or len(graph.vertices) < 2:
        return
    
    # Convert to adjacency list
    adjacency = {v[0]: [] for v in graph.vertices}
    for edge in graph.edges:
        adjacency[edge[0]].append(edge[1])
        adjacency[edge[1]].append(edge[0])
    
    # Initialize random positions
    positions = {}
    for name, _ in graph.vertices:
        positions[name] = [
            random.uniform(100, width - 100),
            random.uniform(100, height - 100)
        ]
    
    # Spring algorithm parameters
    k = math.sqrt((width * height) / len(graph.vertices))  # Optimal distance
    
    for iteration in range(iterations):
        forces = {name: [0, 0] for name in positions}
        
        # Repulsive forces between all pairs
        vertex_names = list(positions.keys())
        for i in range(len(vertex_names)):
            for j in range(i + 1, len(vertex_names)):
                v1, v2 = vertex_names[i], vertex_names[j]
                dx = positions[v1][0] - positions[v2][0]
                dy = positions[v1][1] - positions[v2][1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    force = k * k / distance
                    forces[v1][0] += force * dx / distance
                    forces[v1][1] += force * dy / distance
                    forces[v2][0] -= force * dx / distance
                    forces[v2][1] -= force * dy / distance
        
        # Attractive forces for connected vertices
        for edge in graph.edges:
            v1, v2 = edge
            dx = positions[v1][0] - positions[v2][0]
            dy = positions[v1][1] - positions[v2][1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                force = distance * distance / k
                forces[v1][0] -= force * dx / distance
                forces[v1][1] -= force * dy / distance
                forces[v2][0] += force * dx / distance
                forces[v2][1] += force * dy / distance
        
        # Apply forces
        for name in positions:
            force_magnitude = math.sqrt(forces[name][0]**2 + forces[name][1]**2)
            if force_magnitude > 0:
                # Limit displacement
                displacement = min(force_magnitude, 10)
                positions[name][0] += displacement * forces[name][0] / force_magnitude
                positions[name][1] += displacement * forces[name][1] / force_magnitude
                
                # Keep within bounds
                positions[name][0] = max(50, min(width - 50, positions[name][0]))
                positions[name][1] = max(50, min(height - 50, positions[name][1]))
    
    # Update graph vertices
    for i, (name, _) in enumerate(graph.vertices):
        x, y = positions[name]
        graph.vertices[i] = (name, QPoint(int(x), int(y)))
    
    # Reset control points for all edges
    for edge in graph.edges:
        graph.create_default_control_point(edge)


def format_graph_hierarchical(graph, width=600, height=500):
    """Sắp xếp đồ thị theo cấu trúc phân cấp (BFS-based)"""
    if not graph.vertices:
        return
    
    # Build adjacency list
    adjacency = {v[0]: [] for v in graph.vertices}
    for edge in graph.edges:
        adjacency[edge[0]].append(edge[1])
        adjacency[edge[1]].append(edge[0])
    
    # Find root (vertex with highest degree, or first vertex)
    root = max(graph.vertices, key=lambda v: len(adjacency[v[0]]))[0]
    
    # BFS to create levels
    visited = set()
    levels = {}
    queue = deque([(root, 0)])
    visited.add(root)
    levels[root] = 0
    max_level = 0
    
    while queue:
        vertex, level = queue.popleft()
        max_level = max(max_level, level)
        
        for neighbor in adjacency[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                levels[neighbor] = level + 1
                queue.append((neighbor, level + 1))
    
    # Group vertices by level
    level_groups = {}
    for vertex, level in levels.items():
        if level not in level_groups:
            level_groups[level] = []
        level_groups[level].append(vertex)
    
    # Position vertices
    margin = 80
    level_height = (height - 2 * margin) / (max_level + 1) if max_level > 0 else height - 2 * margin
    
    for level, vertices_in_level in level_groups.items():
        y = margin + level * level_height
        vertex_width = (width - 2 * margin) / len(vertices_in_level) if len(vertices_in_level) > 1 else 0
        
        for i, vertex_name in enumerate(vertices_in_level):
            if len(vertices_in_level) == 1:
                x = width // 2
            else:
                x = margin + i * vertex_width + vertex_width // 2
            
            # Find and update vertex position
            for j, (name, _) in enumerate(graph.vertices):
                if name == vertex_name:
                    graph.vertices[j] = (name, QPoint(int(x), int(y)))
                    break
    
    # Reset control points for all edges
    for edge in graph.edges:
        graph.create_default_control_point(edge)


def export_file(graph, file_path):
    if not file_path:
        return

    data = {
        "vertices": [
            {"name": name, "x": pos.x(), "y": pos.y()}
            for name, pos in graph.vertices
        ],
        "edges": [
            [v1, v2] for v1, v2 in graph.edges
        ],
        "control_points": {
            f"{edge[0]}-{edge[1]}": {"x": point.x(), "y": point.y()}
            for edge, point in graph.edge_control_points.items()
        }
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def import_file(graph, file_path):
    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph.clear()
    
    for v in data.get("vertices", []):
        name = v["name"]
        pos = QPoint(v["x"], v["y"])
        graph.add_vertex((name, pos))
    
    for edge in data.get("edges", []):
        if len(edge) == 2:
            graph.add_edge(tuple(edge))
    
    # Import điểm điều khiển
    control_points = data.get("control_points", {})
    for edge_key, point_data in control_points.items():
        if "-" in edge_key:
            parts = edge_key.split("-")
            if len(parts) == 2:
                edge = (parts[0], parts[1])
                control_point = QPointF(point_data["x"], point_data["y"])
                graph.set_control_point(edge, control_point)

