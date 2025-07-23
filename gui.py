from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit, QSizePolicy, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from graph_area import GraphArea
from graph import Graph
from graph import hamiltonian_cycle
# from graph import dfs_hamiltonian_cycle
# from graph import bfs_hamiltonian_cycle
from graph import generate_random_graph
import pathlib
from PyQt5.QtGui import QIcon
from graph import export_file
from graph import import_file
from graph import connected_components


class GraphGUI(QWidget):
    def __init__(self):
        super().__init__()

        css_path = pathlib.Path("style.css")
        self.setStyleSheet(css_path.read_text(encoding="utf-8"))
        self.graph = Graph()
        self.setWindowTitle("Giải thuật tìm chu trình Hamilton")


        outer_layout = QVBoxLayout(self)

        # Tiêu đề
        heading = QLabel("ỨNG DỤNG VẼ VÀ XỬ LÝ ĐỒ THỊ BẰNG GIẢI THUẬT TÌM CHU TRÌNH HAMILTON")
        heading.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(heading)
        heading.setObjectName("heading")
        self.setWindowIcon(QIcon("4fe7b638f74885de07d05000191aad3d_t.jpeg"))


        main_layout = QHBoxLayout()
        outer_layout.addLayout(main_layout, stretch=4) 

        # === VÙNG VẼ ĐỒ THỊ ===
        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout, stretch=8)

        self.graph_area = GraphArea(self.graph, lambda: self.draw_combo.currentText(), self)
        self.graph_area.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.graph_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        center_layout.addWidget(self.graph_area, stretch=6)


        # Layout dưới vùng vẽ
        bottom_layout = QHBoxLayout()
        center_layout.addLayout(bottom_layout, stretch=2)

        left_output_layout = QVBoxLayout()
        bottom_layout.addLayout(left_output_layout, stretch=1)

        label_result = QLabel("Kết quả xử lý đồ thị:")
        label_result.setStyleSheet("font-weight: bold;")
        left_output_layout.addWidget(label_result)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        left_output_layout.addWidget(self.result_output)

        label_components = QLabel("Bộ phận liên thông:")
        label_components.setStyleSheet("font-weight: bold; margin-top: 5px;")
        left_output_layout.addWidget(label_components)

        self.components = QTextEdit()
        self.components.setReadOnly(True)
        self.components.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        left_output_layout.addWidget(self.components)


        right_info_layout = QVBoxLayout()
        bottom_layout.addLayout(right_info_layout, stretch=1)

        label_info = QLabel("Thông tin đồ thị:")
        label_info.setStyleSheet("font-weight: bold;")
        right_info_layout.addWidget(label_info)

        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        right_info_layout.addWidget(self.info_box)



        # === PANEL ĐIỀU KHIỂN ===
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
        control_panel.setObjectName("control_panel")

        label_draw = QLabel("Lựa chọn vẽ")
        label_draw.setObjectName("label_draw")
        control_panel.addWidget(label_draw)
        self.draw_combo = QComboBox()
        self.draw_combo.addItems(["Thêm đỉnh", "Thêm cạnh", "Xóa"])
        self.draw_combo.setStyleSheet("padding-left: 15px;")
        self.draw_combo.setObjectName("draw_combo")
        control_panel.addWidget(self.draw_combo)

        control_panel.addSpacing(10)
        self.btn_execute = QPushButton("Thực hiện")
        self.btn_components = QPushButton("Bộ phận liên thông")
        self.btn_random = QPushButton("Đồ thị ngẫu nhiên")
        self.btn_clear = QPushButton("Xóa đồ thị")
        for btn in [self.btn_execute, self.btn_components, self.btn_random, self.btn_clear]:
            control_panel.addSpacing(15)
            btn.setFixedHeight(30)
            control_panel.addWidget(btn)
            self.btn_execute.setObjectName("btn_execute")
            self.btn_components.setObjectName("btn_components")
            self.btn_random.setObjectName("btn_random")
            self.btn_clear.setObjectName("btn_clear")

        control_panel.addSpacing(30)
        options_panel = QLabel("Tùy chọn")
        options_panel.setObjectName("options_panel")
        control_panel.addWidget(options_panel)
        self.options_combo = QComboBox()
        self.options_combo.addItems(["Chọn tùy chọn", "Xuất file", "Nhập file", "Xuất ảnh", "Xem thông tin đồ thị"])
        self.options_combo.setStyleSheet("padding-left: 15px;")
        control_panel.addWidget(self.options_combo)
        control_panel.addStretch()

        # Kết nối sự kiện
        self.btn_random.clicked.connect(self.generate_random_graph)
        self.btn_clear.clicked.connect(self.clear_graph)
        self.btn_execute.clicked.connect(self.run_algorithm)
        self.draw_combo.currentTextChanged.connect(self.on_draw_mode_changed)
        self.options_combo.currentTextChanged.connect(self.handle_option_change)
        self.btn_components.clicked.connect(self.run_connected_components)


        

    def generate_random_graph(self):
        generate_random_graph(self.graph, num_vertices=6)
        self.graph_area.selected_vertices.clear()
        self.graph_area.update()
        self.result_output.clear()

    def on_draw_mode_changed(self, mode):
        self.graph_area.selected_vertices.clear()
        self.graph_area.update()


    def clear_graph(self):
        self.graph.clear()
        self.graph_area.selected_vertices.clear()
        self.graph_area.update()
        self.result_output.clear()
        
    def run_algorithm(self):
        if not self.graph.vertices:
            self.result_output.setPlainText("Không có đồ thị để thực hiện.")
            return
    
        algo = self.algorithm_combo.currentText()
        
        if algo == "Quay lui":
            result = hamiltonian_cycle(self.graph)
            if result:
                self.result_output.setPlainText("Chu trình Hamilton tìm được:\n" + " → ".join(result))
            else:
                self.result_output.setPlainText("Không tìm thấy chu trình Hamilton.")
        # elif algo == "Thuật toán DFS":       
        #     result = dfs_hamiltonian_cycle(self.graph)
        #     if result:
        #         self.result_output.setPlainText("Chu trình Hamilton tìm được:\n" + " → ".join(result))
        #     else:
        #         self.result_output.setPlainText("Không tìm thấy chu trình Hamilton.")
        # elif algo == "Thuật toán BFS":
        #     result = bfs_hamiltonian_cycle(self.graph)
        #     if result:
        #         self.result_output.setPlainText("Chu trình Hamilton tìm được:\n" + " → ".join(result))
        #     else:
        #         self.result_output.setPlainText("Không tìm thấy chu trình Hamilton.")

    def run_exportfile(self):
        option = self.options_combo.currentText()
        if option == "Xuất file":
           file_path, _ = QFileDialog.getSaveFileName(self, "Lưu đồ thị", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            export_file(self.graph, file_path)
            QMessageBox.information(self, "Thành công ", "Lưu đồ thị thành công")
    def run_importfile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Nhập đồ thị", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            import_file(self.graph, file_path)
            self.graph_area.selected_vertices.clear()
            self.graph_area.update()
            self.result_output.clear()
        # QMessageBox.information(self, "Thành công", "Đã nhập đồ thị thành công!")
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
        # QMessageBox.information(self, "Thành công", "Đã lưu ảnh đồ thị thành công!")
    def handle_option_change(self, option):
        if option == "Xuất file":
            self.run_exportfile()
        elif option == "Nhập file":
            self.run_importfile()
            self.options_combo.setCurrentIndex(0)
        elif option == "Xuất ảnh":
            self.run_export_image()
            self.options_combo.setCurrentIndex(0)

    def run_connected_components(self):
        if not self.graph.vertices:
            self.components.setPlainText("Không có đồ thị để kiểm tra.")
            return
        num_components = connected_components(self.graph)
        self.components.setPlainText(f"Số miền liên thông: {num_components}")





