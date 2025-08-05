from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QSizePolicy, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from graph_area import GraphArea
from graph import Graph
from graph import generate_random_graph, export_file, import_file, format_graph_circular, format_graph_grid, format_graph_spring, format_graph_hierarchical
from graph_algorithms import hamiltonian_cycle_with_steps, connected_components
from PyQt5.QtGui import QIcon
import pathlib

class GraphGUI(QWidget):
    def __init__(self):
        super().__init__()

        css_path = pathlib.Path("style.css")
        try:
            self.setStyleSheet(css_path.read_text(encoding="utf-8"))
        except:
            pass
            
        self.graph = Graph()
        self.setWindowTitle("Giải thuật tìm chu trình Hamilton")
        self.hamilton_steps = [] 
        self.is_step_mode = False

        outer_layout = QVBoxLayout(self)
        heading = QLabel("ỨNG DỤNG VẼ VÀ XỬ LÝ ĐỒ THỊ BẰNG GIẢI THUẬT TÌM CHU TRÌNH HAMILTON")
        heading.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(heading)
        heading.setObjectName("heading")
        try:
            self.setWindowIcon(QIcon("4fe7b638f74885de07d05000191aad3d_t.jpeg"))
        except:
            pass

        main_layout = QHBoxLayout()
        outer_layout.addLayout(main_layout, stretch=4) 

        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout, stretch=8)

        self.graph_area = GraphArea(self.graph, lambda: self.draw_combo.currentText(), self)
        self.graph_area.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.graph_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center_layout.addWidget(self.graph_area, stretch=3)

        bottom_layout = QHBoxLayout()
        center_layout.addLayout(bottom_layout, stretch=2)

        result_layout = QVBoxLayout()
        bottom_layout.addLayout(result_layout, stretch=1)

        label_result = QLabel("Kết quả xử lý đồ thị:")
        label_result.setStyleSheet("font-weight: bold;")
        result_layout.addWidget(label_result)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        result_layout.addWidget(self.result_output)

        info_layout = QVBoxLayout()
        bottom_layout.addLayout(info_layout, stretch=1)

        label_info = QLabel("Thông tin đồ thị:")
        label_info.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(label_info)

        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        info_layout.addWidget(self.info_box)

        component_layout = QVBoxLayout()
        bottom_layout.addLayout(component_layout, stretch=1)

        label_components = QLabel("Miền liên thông:")
        label_components.setStyleSheet("font-weight: bold;")
        component_layout.addWidget(label_components)

        self.components = QTextEdit()
        self.components.setReadOnly(True)
        self.components.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        component_layout.addWidget(self.components)

        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignTop)
        main_layout.addLayout(control_panel, stretch=2)

        label_algo = QLabel("Chọn giải thuật")
        label_algo.setObjectName("label_algo")
        control_panel.addWidget(label_algo) 
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Quay lui"])
        self.algorithm_combo.setStyleSheet("padding-left: 15px;")
        self.algorithm_combo.setObjectName("algorithm_combo")
        control_panel.addWidget(self.algorithm_combo)

        label_draw = QLabel("Lựa chọn vẽ")
        label_draw.setObjectName("label_draw")
        control_panel.addWidget(label_draw)
        self.draw_combo = QComboBox()
        self.draw_combo.addItems(["Thêm đỉnh", "Thêm cạnh", "Xóa"])
        self.draw_combo.setStyleSheet("padding-left: 15px;")
        self.draw_combo.setObjectName("draw_combo")
        control_panel.addWidget(self.draw_combo)

        self.instruction_label = QLabel("")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setStyleSheet("color: #666; font-size: 11px; margin: 5px;")
        control_panel.addWidget(self.instruction_label)

        control_panel.addSpacing(10)
        self.btn_execute = QPushButton("Thực hiện")
        self.btn_components = QPushButton("Miền liên thông")
        self.btn_random = QPushButton("Đồ thị ngẫu nhiên")
        self.btn_format = QPushButton("Format đồ thị")
        self.btn_clear = QPushButton("Xóa đồ thị")
        
        for btn in [self.btn_execute, self.btn_components, self.btn_random, self.btn_format, self.btn_clear]:
            control_panel.addSpacing(15)
            btn.setFixedHeight(30)
            control_panel.addWidget(btn)
            if btn == self.btn_execute:
                btn.setObjectName("btn_execute")
            elif btn == self.btn_components:
                btn.setObjectName("btn_components")
            elif btn == self.btn_random:
                btn.setObjectName("btn_random")
            elif btn == self.btn_format:
                btn.setObjectName("btn_format")
            elif btn == self.btn_clear:
                btn.setObjectName("btn_clear")

        control_panel.addSpacing(30)
        options_panel = QLabel("Tùy chọn")
        options_panel.setObjectName("options_panel")
        control_panel.addWidget(options_panel)
        self.options_combo = QComboBox()
        self.options_combo.addItems(["Chọn tùy chọn", "Xuất file", "Nhập file", "Xuất ảnh", "Xem thông tin đồ thị", "Thực hiện từng bước"])
        self.options_combo.setStyleSheet("padding-left: 15px;")
        control_panel.addWidget(self.options_combo)

        control_panel.addSpacing(10)
        label_start_vertex = QLabel("Chọn đỉnh bắt đầu")
        label_start_vertex.setObjectName("label_start_vertex")
        control_panel.addWidget(label_start_vertex)
        self.start_vertex_combo = QComboBox()
        self.start_vertex_combo.addItem("Mặc định")
        self.start_vertex_combo.setStyleSheet("padding-left: 15px;")
        self.start_vertex_combo.setObjectName("start_vertex_combo")
        control_panel.addWidget(self.start_vertex_combo)

        control_panel.addStretch()

        self.btn_random.clicked.connect(self.generate_random_graph)
        self.btn_clear.clicked.connect(self.clear_graph)
        self.btn_execute.clicked.connect(self.run_algorithm)
        self.draw_combo.currentTextChanged.connect(self.on_draw_mode_changed)
        self.options_combo.currentTextChanged.connect(self.handle_option_change)
        self.btn_components.clicked.connect(self.run_connected_components)
        self.btn_format.clicked.connect(self.auto_format_graph)
        self.update_instructions()
        self.update_vertex_combo()

    def update_instructions(self):
        mode = self.draw_combo.currentText()
        instructions = {
            "Thêm đỉnh": "Double-click để thêm đỉnh mới",
            "Thêm cạnh": "Giữ Shift + click chọn 2 đỉnh để nối cạnh",
            "Xóa": "Click vào đỉnh hoặc cạnh để xóa"
        }
        base_instruction = instructions.get(mode, "")
        curve_instruction = "Kéo trên cạnh để làm cong"
        self.instruction_label.setText(f"{base_instruction}\n{curve_instruction}")

    def update_vertex_combo(self):
        """Update the vertex selection combo box with current graph vertices."""
        self.start_vertex_combo.clear()
        self.start_vertex_combo.addItem("Mặc định")
        for name, _ in self.graph.vertices:
            self.start_vertex_combo.addItem(name)

    def exit_step_mode(self):
        """Khởi động lại chế độ thực hiện từng bước và xóa kết quả hiển thị"""
        self.is_step_mode = False
        self.hamilton_steps = []
        self.result_output.setPlainText("")

    def auto_format_graph(self):
        if not self.graph.vertices:
            QMessageBox.information(self, "Thông báo", "Không có đồ thị để format.")
            return
        self.graph_area.push_undo()
        width = self.graph_area.width()
        height = self.graph_area.height()
        num_vertices = len(self.graph.vertices)
        num_edges = len(self.graph.edges)
        if num_vertices <= 8 and num_edges >= num_vertices - 1:
            format_graph_circular(self.graph, width, height)
            layout_name = "Hình tròn"
        elif num_edges < num_vertices * 0.3:
            if self.is_tree_like():
                format_graph_hierarchical(self.graph, width, height)
                layout_name = "Phân cấp"
            else:
                format_graph_grid(self.graph, width, height)
                layout_name = "Lưới"
        else:
            format_graph_spring(self.graph, width, height)
            layout_name = "Spring (Tự động)"
        self.graph_area.update()
        self.update_vertex_combo()
        QMessageBox.information(self, "Thành công", f"Đã format đồ thị theo kiểu {layout_name}.")

    def is_tree_like(self):
        num_vertices = len(self.graph.vertices)
        num_edges = len(self.graph.edges)
        if num_edges == num_vertices - 1:
            return connected_components(self.graph) == 1
        return False

    def generate_random_graph(self):
        self.graph_area.push_undo()
        generate_random_graph(self.graph, num_vertices=6)
        self.graph_area.selected_vertices.clear()
        self.graph_area.clear_hamilton_visualization()
        self.graph_area.update()
        self.result_output.clear()
        self.components.clear()
        self.info_box.clear()
        self.hamilton_steps = []
        self.is_step_mode = False
        self.update_vertex_combo()

    def on_draw_mode_changed(self, mode):
        self.graph_area.selected_vertices.clear()
        self.graph_area.update()
        self.update_instructions()

    def clear_graph(self):
        self.graph_area.push_undo()
        self.graph.clear()
        self.graph_area.selected_vertices.clear()
        self.graph_area.clear_hamilton_visualization()
        self.graph_area.update()
        self.result_output.clear()
        self.components.clear()
        self.info_box.clear()
        self.hamilton_steps = []
        self.is_step_mode = False
        self.update_vertex_combo()

    def run_algorithm(self):
        if not self.graph.vertices:
            self.result_output.setPlainText("Không có đồ thị để thực hiện.")
            self.graph_area.clear_hamilton_visualization()
            self.hamilton_steps = []
            self.is_step_mode = False
            return
        algo = self.algorithm_combo.currentText()
        if algo == "Quay lui":
            start_vertex = self.start_vertex_combo.currentText()
            if start_vertex == "Mặc định":
                start_vertex = None
            result = hamiltonian_cycle_with_steps(self.graph, start_vertex=start_vertex)
            self.hamilton_steps = result['steps']
            if self.is_step_mode:
                self.graph_area.set_hamilton_steps(self.hamilton_steps)
                self.update_step_display(0)
            else:
                self.graph_area.set_hamilton_visualization(result['path'])
                if result['success']:
                    output = "Chu trình Hamilton tìm được:\n" + " → ".join(result['path']) + "\n\n"
                    output += "Các bước thực hiện:\n"
                    for step in result['steps']:
                        output += f"{step['action']}\n"
                    output += f"\nTổng số bước: {result['total_steps']}"
                    self.result_output.setPlainText(output)
                else:
                    output = "Không tìm thấy chu trình Hamilton.\n\nCác bước thực hiện:\n"
                    for step in result['steps']:
                        output += f"{step['action']}\n"
                    output += f"\nTổng số bước: {result['total_steps']}"
                    self.result_output.setPlainText(output)

    def update_step_display(self, step_index):
        """Update result text based on the current step"""
        if not self.hamilton_steps or step_index < 0 or step_index >= len(self.hamilton_steps):
            self.result_output.setPlainText("")
            return
        step = self.hamilton_steps[step_index]
        output = f"Bước {step['step']}: {step['action']}\n"
        output += f"Đường đi hiện tại: {' → '.join(step['path']) if step['path'] else 'Rỗng'}\n"
        output += f"Tổng số bước: {len(self.hamilton_steps)}"
        self.result_output.setPlainText(output)

    def run_exportfile(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu đồ thị", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            export_file(self.graph, file_path)
            QMessageBox.information(self, "Thành công", "Lưu đồ thị thành công!")
    
    def run_importfile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Nhập đồ thị", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                self.graph_area.push_undo()
                import_file(self.graph, file_path)
                self.graph_area.selected_vertices.clear()
                self.graph_area.clear_hamilton_visualization()
                self.graph_area.update()
                self.result_output.clear()
                self.components.clear()
                self.hamilton_steps = []
                self.is_step_mode = False
                self.update_vertex_combo()
                QMessageBox.information(self, "Thành công", "Nhập đồ thị thành công!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể nhập file: {str(e)}")

    def update_graph_info(self):
        if not self.graph.vertices:
            self.info_box.setPlainText("Không có đồ thị để hiển thị thông tin.")
            return
        num_vertices = len(self.graph.vertices)
        num_edges = len(self.graph.edges)
        vertex_names = [name for name, _ in self.graph.vertices]
        info_text = f"Số đỉnh: {num_vertices}\n"
        info_text += f"Số cạnh: {num_edges}\n"
        info_text += f"Danh sách đỉnh: {', '.join(vertex_names)}\n"
        if self.graph.edges:
            edge_list = [f"{u}-{v}" for u, v in self.graph.edges]
            info_text += f"Danh sách cạnh: {', '.join(edge_list)}\n"
        info_text += "\nMa trận kề:\n"
        matrix = self.build_adjacency_matrix()
        headers = [name for name, _ in self.graph.vertices]
        info_text += "   " + "  ".join(headers) + "\n"
        for i, row in enumerate(matrix):
            info_text += headers[i] + "  " + "  ".join(str(cell) for cell in row) + "\n"
        info_text += "\nBậc của từng đỉnh:\n"
        for i, row in enumerate(matrix):
            degree = sum(row)
            info_text += f"Đỉnh {headers[i]}: {degree}\n"
        self.info_box.setPlainText(info_text)

    def build_adjacency_matrix(self):
        vertices = [name for name, _ in self.graph.vertices]
        idx_map = {name: i for i, name in enumerate(vertices)}
        n = len(vertices)
        matrix = [[0] * n for _ in range(n)]
        for u, v in self.graph.edges:
            i, j = idx_map[u], idx_map[v]
            matrix[i][j] = 1
            matrix[j][i] = 1
        return matrix

    def handle_option_change(self, option):
        if option == "Xuất file":
            self.run_exportfile()
            self.options_combo.setCurrentIndex(0)
        elif option == "Nhập file":
            self.run_importfile()
            self.options_combo.setCurrentIndex(0)
        elif option == "Xuất ảnh":
            self.run_export_image()
            self.options_combo.setCurrentIndex(0)
        elif option == "Xem thông tin đồ thị":
            self.update_graph_info()
            self.options_combo.setCurrentIndex(0)
        elif option == "Thực hiện từng bước":
            self.is_step_mode = True
            self.run_algorithm()
            self.options_combo.setCurrentIndex(0)

    def run_connected_components(self):
        if not self.graph.vertices:
            self.components.setPlainText("Không có đồ thị để kiểm tra.")
            return
        num_components = connected_components(self.graph)
        self.components.setPlainText(f"Số miền liên thông: {num_components}")
    
    def run_export_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu ảnh đồ thị",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)"
        )
        if file_path:
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                image_format = "JPEG"
            else:
                image_format = "PNG"
            self.graph_area.grab().save(file_path, image_format)
            QMessageBox.information(self, "Thành công", "Đã lưu ảnh đồ thị thành công!")