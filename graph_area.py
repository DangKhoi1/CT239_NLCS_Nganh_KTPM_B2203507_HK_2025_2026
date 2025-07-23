from math import hypot
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

    def keyReleaseEvent(self, event):
        if self.get_mode() == "Thêm cạnh" and event.key() == Qt.Key_Shift:
            if self.selected_vertices:
                self.selected_vertices.clear()
                self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        pos = event.pos()
        mode = self.get_mode()

        for i, (name, vpos) in enumerate(self.graph.vertices):
            if (pos - vpos).manhattanLength() <= 20:
                self.selected_vertex_idx = i
                break

        if mode == "Thêm đỉnh":
            if event.type() == event.MouseButtonDblClick:
                name, ok = QInputDialog.getText(self, "Thêm đỉnh", "Nhập tên đỉnh:")
                if ok and name:
                    self.graph.add_vertex((name, pos))
                    self.update()

        elif mode == "Thêm cạnh":
            for name, vpos in self.graph.vertices:
                if (pos - vpos).manhattanLength() <= 20:
                    if event.modifiers() & Qt.ShiftModifier:
                        self.selected_vertices.append(name)
                        if len(self.selected_vertices) == 2:
                            self.graph.add_edge(tuple(self.selected_vertices))
                            self.selected_vertices.clear()
                        self.update()
                    return

        elif mode == "Xóa":
            for i, (name, vpos) in enumerate(self.graph.vertices):
                if (pos - vpos).manhattanLength() <= 20:
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
                        self.graph.remove_edge((name1, name2))
                        self.selected_vertices.clear()
                        self.update()
                        return
                else:
                    if self.is_point_near_line(pos, pos1, pos2, 10):
                        self.graph.remove_edge((name1, name2))
                        self.selected_vertices.clear()
                        self.update()
                        return


    def mouseMoveEvent(self, event):
        if self.selected_vertex_idx is not None:
            if 0 <= self.selected_vertex_idx < len(self.graph.vertices):
                name, _ = self.graph.vertices[self.selected_vertex_idx]
                self.graph.vertices[self.selected_vertex_idx] = (name, event.pos())
                self.update()
            else:
                self.selected_vertex_idx = None

    def mouseReleaseEvent(self, event):
        self.selected_vertex_idx = None

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

        pen = QPen(Qt.black)
        pen.setWidth(3)
        painter.setPen(pen)

        mode = self.get_mode()

        # Vẽ các cạnh
        for start, end in self.graph.edges:
            pos1 = next((pos for name, pos in self.graph.vertices if name == start), None)
            pos2 = next((pos for name, pos in self.graph.vertices if name == end), None)

            if pos1 is None or pos2 is None:
                continue

            painter.setPen(QPen(Qt.black, 3))

            if start == end:
                # Vẽ self-loop dạng cong móc tại đỉnh
                path = QPainterPath()
                path.moveTo(pos1)

                dx, dy = 60, -60  # Điều chỉnh độ cong
                ctrl1 = QPointF(pos1.x() + dx, pos1.y() + dy)
                ctrl2 = QPointF(pos1.x() - dx, pos1.y() + dy)
                path.cubicTo(ctrl1, ctrl2, pos1)

                painter.drawPath(path)
            else:
                # Vẽ cạnh thường
                painter.drawLine(pos1, pos2)

        # Làm nổi bật đỉnh đang chọn nếu đang thêm cạnh
        highlight = self.selected_vertices if mode == "Thêm cạnh" else []

        for name, pos in self.graph.vertices:
            if name in highlight:
                pen = QPen(Qt.red)
                pen.setWidth(4)
                brush = QBrush(QColor("yellow"))
            else:
                pen = QPen(Qt.black)
                pen.setWidth(3)
                brush = QBrush(QColor("white"))

            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawEllipse(pos, 20, 20)

            rect = QRect(pos.x() - 20, pos.y() - 20, 40, 40)
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, name)
