from math import hypot
from copy import deepcopy
from PyQt5.QtWidgets import QWidget, QInputDialog
from PyQt5.QtCore import Qt, QRect, QPointF
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QPainterPath


class GraphArea(QWidget):
    def __init__(self, graph, mode_getter, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.get_mode = mode_getter
        self.setFocusPolicy(Qt.StrongFocus)
        self.selected_vertex_idx = None
        self.selected_vertices = []
        self.selecting_area = False
        self.selection_start = QPointF()
        self.selection_end = QPointF()
        self.area_selected_vertices = []
        self.area_selected_edges = []
        self.last_mouse_pos = None  
        self.undo_stack = []  
        self.redo_stack = []  

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.push_undo()
            self.delete_selected()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_C:
            self.copy_selection()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_V:
            self.push_undo()
            self.paste_selection()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
            self.undo()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.redo()

        if self.get_mode() == "Thêm cạnh" and event.key() == Qt.Key_Shift:
            self.selected_vertices.clear()
            self.update()

    def push_undo(self):
        self.undo_stack.append((deepcopy(self.graph.vertices), deepcopy(self.graph.edges)))
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append((deepcopy(self.graph.vertices), deepcopy(self.graph.edges)))
            vertices, edges = self.undo_stack.pop()
            self.graph.vertices = vertices
            self.graph.edges = edges
            self.update()

    def redo(self):
        if self.redo_stack:
            self.push_undo()
            vertices, edges = self.redo_stack.pop()
            self.graph.vertices = vertices
            self.graph.edges = edges
            self.update()
    def redo(self):
        if not self.redo_stack:
            return  
        self.undo_stack.append((deepcopy(self.graph.vertices), deepcopy(self.graph.edges)))
        vertices, edges = self.redo_stack.pop()
        self.graph.vertices = vertices
        self.graph.edges = edges
        self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        pos = event.pos()
        self.last_mouse_pos = pos  
        mode = self.get_mode()

        self.selected_vertex_idx = None
        for i, (name, vpos) in enumerate(self.graph.vertices):
            if (pos - vpos).manhattanLength() <= 20:
                self.selected_vertex_idx = i
                break

        if self.selected_vertex_idx is None:
            self.selecting_area = True
            self.selection_start = pos
            self.selection_end = pos
            self.update()

        if mode == "Thêm đỉnh" and event.type() == event.MouseButtonDblClick:
            name, ok = QInputDialog.getText(self, "Thêm đỉnh", "Nhập tên đỉnh:")
            if ok and name:
                self.push_undo()
                self.graph.add_vertex((name, pos))
                self.update()

        if mode == "Thêm cạnh":
            for name, vpos in self.graph.vertices:
                if (pos - vpos).manhattanLength() <= 20:
                    if event.modifiers() & Qt.ShiftModifier:
                        self.selected_vertices.append(name)
                        if len(self.selected_vertices) == 2:
                            self.push_undo()
                            self.graph.add_edge(tuple(self.selected_vertices))
                            self.selected_vertices.clear()
                        self.update()
                    return

        if mode == "Xóa":
            for i, (name, vpos) in enumerate(self.graph.vertices):
                if (pos - vpos).manhattanLength() <= 20:
                    self.push_undo()
                    self.graph.remove_vertex((name, vpos))
                    self.selected_vertices.clear()
                    self.update()
                    return

            for name1, name2 in self.graph.edges:
                pos1 = next((v for n, v in self.graph.vertices if n == name1), None)
                pos2 = next((v for n, v in self.graph.vertices if n == name2), None)
                if not pos1 or not pos2:
                    continue

                if name1 == name2:
                    control_point = QPointF(pos1.x(), pos1.y() - 40)
                    if self.is_point_near_line(pos, pos1, control_point, 15):
                        self.push_undo()
                        self.graph.remove_edge((name1, name2))
                        self.selected_vertices.clear()
                        self.update()
                        return
                else:
                    if self.is_point_near_line(pos, pos1, pos2, 10):
                        self.push_undo()
                        self.graph.remove_edge((name1, name2))
                        self.selected_vertices.clear()
                        self.update()
                        return

    def mouseMoveEvent(self, event):
        if not self.selecting_area and self.area_selected_vertices:
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()
            self.last_mouse_pos = event.pos()
            for i, (name, pos) in enumerate(self.graph.vertices):
                if name in self.area_selected_vertices:
                    self.graph.vertices[i] = (name, QPointF(pos.x() + dx, pos.y() + dy))
            self.update()
            return

        if self.selected_vertex_idx is not None:
            if 0 <= self.selected_vertex_idx < len(self.graph.vertices):
                name, _ = self.graph.vertices[self.selected_vertex_idx]
                self.graph.vertices[self.selected_vertex_idx] = (name, event.pos())
                self.update()
        elif self.selecting_area:
            self.selection_end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.selected_vertex_idx = None
        self.last_mouse_pos = None  

        if self.selecting_area:
            self.selecting_area = False
            self.area_selected_vertices.clear()
            self.area_selected_edges.clear()

            rect = QRect(
                self.selection_start.toPoint() if isinstance(self.selection_start, QPointF) else self.selection_start,
                self.selection_end.toPoint() if isinstance(self.selection_end, QPointF) else self.selection_end
            ).normalized()

            for name, pos in self.graph.vertices:
                if rect.contains(pos.toPoint() if isinstance(pos, QPointF) else pos):
                    self.area_selected_vertices.append(name)

            for name1, name2 in self.graph.edges:
                pos1 = next((p for n, p in self.graph.vertices if n == name1), None)
                pos2 = next((p for n, p in self.graph.vertices if n == name2), None)
                if pos1 and pos2 and rect.contains(pos1.toPoint() if isinstance(pos1, QPointF) else pos1) \
                        and rect.contains(pos2.toPoint() if isinstance(pos2, QPointF) else pos2):
                    self.area_selected_edges.append((name1, name2))

            self.update()

    def delete_selected(self):
        self.graph.vertices = [(n, p) for (n, p) in self.graph.vertices if n not in self.area_selected_vertices]
        self.graph.edges = [(a, b) for (a, b) in self.graph.edges if a not in self.area_selected_vertices and b not in self.area_selected_vertices]
        self.area_selected_vertices.clear()
        self.area_selected_edges.clear()
        self.update()

    def copy_selection(self):
        self._copied = [
            (name, pos) for name, pos in self.graph.vertices if name in self.area_selected_vertices
        ]

    def paste_selection(self):
        if not hasattr(self, '_copied') or not self._copied:
            return
        offset = QPointF(40, 40)
        new_names = []
        base_names = set(n for n, _ in self.graph.vertices)
        for name, pos in self._copied:
            new_name = name
            i = 1
            while new_name in base_names:
                new_name = f"{name}_{i}"
                i += 1
            base_names.add(new_name)
            self.graph.vertices.append((new_name, pos + offset))
            new_names.append((name, new_name))

        old_to_new = dict(new_names)
        for a, b in self.graph.edges:
            if a in old_to_new and b in old_to_new:
                self.graph.edges.append((old_to_new[a], old_to_new[b]))
        self.update()

    def is_point_near_line(self, p, a, b, tolerance=10):
        ab = b - a
        ap = p - a
        ab_len_sq = ab.x() ** 2 + ab.y() ** 2
        if ab_len_sq == 0:
            return (p - a).manhattanLength() <= tolerance
        t = max(0, min(1, (ap.x() * ab.x() + ap.y() * ab.y()) / ab_len_sq))
        projection = a + ab * t
        dx = projection.x() - p.x()
        dy = projection.y() - p.y()
        return hypot(dx, dy) <= tolerance

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        mode = self.get_mode()

        for start, end in self.graph.edges:
            pos1 = next((p for n, p in self.graph.vertices if n == start), None)
            pos2 = next((p for n, p in self.graph.vertices if n == end), None)
            if not pos1 or not pos2:
                continue

            color = QColor("deepskyblue") if (start, end) in self.area_selected_edges or (end, start) in self.area_selected_edges else Qt.black
            painter.setPen(QPen(color, 3))

            if start == end:
                path = QPainterPath()
                path.moveTo(pos1)
                ctrl1 = QPointF(pos1.x() + 60, pos1.y() - 60)
                ctrl2 = QPointF(pos1.x() - 60, pos1.y() - 60)
                path.cubicTo(ctrl1, ctrl2, pos1)
                painter.drawPath(path)
            else:
                painter.drawLine(pos1, pos2)

        highlight = self.selected_vertices if mode == "Thêm cạnh" else []

        for name, pos in self.graph.vertices:
            if name in highlight:
                pen = QPen(Qt.red, 4)
                brush = QBrush(QColor("yellow"))
            elif name in self.area_selected_vertices:
                pen = QPen(QColor("deepskyblue"), 4)
                brush = QBrush(Qt.white)
            else:
                pen = QPen(Qt.black, 3)
                brush = QBrush(Qt.white)

            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawEllipse(pos, 20, 20)

            label_rect = QRect(int(pos.x()) - 20, int(pos.y()) - 20, 40, 40)
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(label_rect, Qt.AlignCenter, name)

        if self.selecting_area:
            painter.setPen(QPen(QColor(0, 120, 215, 200), 1, Qt.SolidLine))
            painter.setBrush(QBrush(QColor(0, 120, 215, 60)))
            selection_rect = QRect(
                self.selection_start.toPoint() if isinstance(self.selection_start, QPointF) else self.selection_start,
                self.selection_end.toPoint() if isinstance(self.selection_end, QPointF) else self.selection_end
            ).normalized()
            painter.drawRect(selection_rect)
