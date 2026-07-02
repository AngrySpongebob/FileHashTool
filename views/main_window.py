import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit, QComboBox,
                               QTextEdit, QProgressBar, QGroupBox, QMessageBox, QFrame)


class MainWindow(QMainWindow):
    """主窗口视图"""
    # 用户交互信号
    file_dropped = Signal(str)  # 文件拖拽信号
    file_browsed = Signal()  # 浏览文件信号
    calculate_requested = Signal()  # 计算请求信号
    clear_requested = Signal()  # 清空信号
    copy_requested = Signal()  # 复制信号
    algorithm_changed = Signal(str)  # 算法变更信号

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_drag_drop()

    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("文件HASH校验工具 v2.0")
        self.setMinimumSize(800, 600)

        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title_label = QLabel("文件HASH校验工具")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()

        # 文件路径输入
        path_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("请选择文件或拖拽文件到此处")
        self.file_path_input.setMinimumHeight(30)

        self.browse_btn = QPushButton("浏览文件")
        self.browse_btn.setMinimumHeight(30)
        self.browse_btn.clicked.connect(self._on_browse_clicked)

        path_layout.addWidget(self.file_path_input)
        path_layout.addWidget(self.browse_btn)
        file_layout.addLayout(path_layout)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # 文件信息区域
        info_group = QGroupBox("文件信息")
        info_layout = QVBoxLayout()

        # 文件名字段
        name_layout = QHBoxLayout()
        name_label = QLabel("文件名:")
        name_label.setFixedWidth(80)
        self.file_name_label = QLabel("未选择")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.file_name_label)
        name_layout.addStretch()
        info_layout.addLayout(name_layout)

        # 文件大小字段
        size_layout = QHBoxLayout()
        size_label = QLabel("文件大小:")
        size_label.setFixedWidth(80)
        self.file_size_label = QLabel("未选择")
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.file_size_label)
        size_layout.addStretch()
        info_layout.addLayout(size_layout)

        # 修改时间字段
        time_layout = QHBoxLayout()
        time_label = QLabel("修改时间:")
        time_label.setFixedWidth(80)
        self.file_time_label = QLabel("未选择")
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.file_time_label)
        time_layout.addStretch()
        info_layout.addLayout(time_layout)

        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # HASH选项区域
        hash_group = QGroupBox("HASH选项")
        hash_layout = QVBoxLayout()

        # 算法选择
        algo_layout = QHBoxLayout()
        algo_label = QLabel("HASH算法:")
        algo_label.setFixedWidth(80)

        self.algo_combo = QComboBox()
        from models.hash_model import HashAlgorithm
        self.algo_combo.addItems(HashAlgorithm.get_all_values())
        self.algo_combo.setCurrentText("SHA256")
        self.algo_combo.currentTextChanged.connect(self._on_algorithm_changed)

        algo_hint = QLabel("(推荐使用SHA256或SHA512)")
        algo_hint.setStyleSheet("color: gray;")

        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        algo_layout.addWidget(algo_hint)
        algo_layout.addStretch()
        hash_layout.addLayout(algo_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        hash_layout.addWidget(self.progress_bar)

        hash_group.setLayout(hash_layout)
        main_layout.addWidget(hash_group)

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.calc_btn = QPushButton("获取HASH")
        self.calc_btn.setMinimumHeight(35)
        self.calc_btn.clicked.connect(self._on_calculate_clicked)

        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.setMinimumHeight(35)
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        self.copy_btn = QPushButton("复制HASH")
        self.copy_btn.setMinimumHeight(35)
        self.copy_btn.clicked.connect(self._on_copy_clicked)

        # 为计算按钮设置特殊样式
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        btn_layout.addWidget(self.calc_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # HASH结果显示区域
        result_group = QGroupBox("HASH结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        self.result_text.setMinimumHeight(150)
        self.result_text.setPlaceholderText("请选择文件后点击'获取HASH'按钮")

        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setFrameStyle(QFrame.Sunken | QFrame.Panel)
        self.status_label.setMinimumHeight(25)
        main_layout.addWidget(self.status_label)

        # 应用样式
        self.apply_style()

    def apply_style(self):
        """应用样式表"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 5px 15px;
                border-radius: 3px;
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #d4d4d4;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                min-width: 100px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #fafafa;
            }
        """)

    def setup_drag_drop(self):
        """设置拖拽支持"""
        self.setAcceptDrops(True)
        self.file_path_input.setAcceptDrops(True)
        self.file_path_input.installEventFilter(self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path and os.path.exists(file_path):
                    self.file_dropped.emit(file_path)
                    event.accept()
                    return
        event.ignore()

    def _on_browse_clicked(self):
        """浏览文件按钮点击"""
        self.file_browsed.emit()

    def _on_calculate_clicked(self):
        """计算按钮点击"""
        self.calculate_requested.emit()

    def _on_clear_clicked(self):
        """清空按钮点击"""
        self.clear_requested.emit()

    def _on_copy_clicked(self):
        """复制按钮点击"""
        self.copy_requested.emit()

    def _on_algorithm_changed(self, text: str):
        """算法改变"""
        self.algorithm_changed.emit(text)

    # 更新UI的方法
    def update_file_info(self, file_info: dict):
        """更新文件信息显示"""
        self.file_path_input.setText(file_info['path'])
        self.file_name_label.setText(file_info['name'])
        self.file_size_label.setText(file_info['size_formatted'])
        self.file_time_label.setText(file_info['modified_time'])

    def update_progress(self, value: int):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)

    def show_hash_result(self, algorithm: str, hash_value: str):
        """显示HASH结果"""
        from datetime import datetime
        import os

        file_name = os.path.basename(self.file_path_input.text())
        result = f"文件: {file_name}\n"
        result += f"算法: {algorithm}\n"
        result += "=" * 60 + "\n"
        result += f"HASH值: {hash_value}\n"
        result += "=" * 60 + "\n"
        result += f"计算时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.result_text.setText(result)

    def clear_result(self):
        """清空结果显示"""
        self.result_text.clear()
        self.progress_bar.setValue(0)

    def show_error(self, error: str):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", error)

    def show_warning(self, title: str, warning: str):
        """显示警告信息"""
        QMessageBox.warning(self, title, warning)

    def show_info(self, title: str, message: str):
        """显示信息对话框"""
        QMessageBox.information(self, title, message)

    def set_calculating_state(self, is_calculating: bool):
        """设置计算状态"""
        self.calc_btn.setEnabled(not is_calculating)
        self.browse_btn.setEnabled(not is_calculating)
        self.algo_combo.setEnabled(not is_calculating)

    def get_selected_algorithm(self) -> str:
        """获取当前选择的算法"""
        return self.algo_combo.currentText()

    def get_hash_text(self) -> str:
        """获取HASH文本"""
        return self.result_text.toPlainText()

    def enable_copy_button(self, enabled: bool):
        """启用/禁用复制按钮"""
        self.copy_btn.setEnabled(enabled)
