from collections import deque
import math
import random
from PyQt5.QtCore import QPoint
import json

class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = []

    def add_vertex(self, vertex):
        name, _ = vertex
        if name not in [v[0] for v in self.vertices]:
            self.vertices.append(vertex)

    def add_edge(self, edge):
        name1, name2 = edge
        if {name1, name2} not in [{e[0], e[1]} for e in self.edges]:
            self.edges.append(edge)

    def remove_vertex(self, vertex):
        name, _ = vertex
        self.vertices = [v for v in self.vertices if v[0] != name]
        self.edges = [e for e in self.edges if name not in e]

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def clear(self):
        self.vertices.clear()
        self.edges.clear()
    

def dfs_hamiltonian_cycle(self):
    vertices = [v[0] for v in self.vertices]
    adjacency = {v: set() for v in vertices}
    for u, v in self.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    path = []

    def dfs(v):
        if len(path) == len(vertices):
            return path[0] in adjacency[path[-1]]  # có cạnh về lại đỉnh đầu không
        for neighbor in adjacency[v]:
            if neighbor not in path:
                path.append(neighbor)
                if dfs(neighbor):
                    return True
                path.pop()
        return False

    for start in vertices:
        path.clear()
        path.append(start)
        if dfs(start):
            return path + [path[0]]
    return None



def generate_random_graph(graph, num_vertices=6, edge_probability=0.4, width=600, height=500):
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


def hamiltonian_cycle(graph):
    vertices = [v[0] for v in graph.vertices]
    adjacency = {v: set() for v in vertices}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    path = [vertices[0]]

    def backtrack(pos):
        if len(path) == len(vertices):
            return path[0] in adjacency[path[-1]]  # Có cạnh về đầu không
        for v in vertices:
            if v not in path and v in adjacency[path[-1]]:
                path.append(v)
                if backtrack(pos + 1):
                    return True
                path.pop()
        return False

    if backtrack(1):
        return path + [path[0]]
    return None

def bfs_hamiltonian_cycle(self):
    vertices = [v[0] for v in self.vertices]
    n = len(vertices)
    adjacency = {v: set() for v in vertices}
    for u, v in self.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    for start in vertices:
        queue = deque()
        queue.append((start, [start]))

        while queue:
            current, path = queue.popleft()

            if len(path) == n:
                if path[0] in adjacency[current]:
                    return path + [path[0]]  # chu trình khép kín
                continue

            for neighbor in adjacency[current]:
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

    return None

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
        ]
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
