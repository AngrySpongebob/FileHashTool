from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QFileDialog

from models.hash_model import HashModel, HashAlgorithm
from views.main_window import MainWindow


class HashController(QObject):
    """HASH校验控制器"""

    def __init__(self, model: HashModel, view: MainWindow):
        super().__init__()
        self.model = model
        self.view = view

        # 连接视图信号
        self.view.file_dropped.connect(self._on_file_selected)
        self.view.file_browsed.connect(self._on_browse_file)
        self.view.calculate_requested.connect(self._on_calculate)
        self.view.clear_requested.connect(self._on_clear)
        self.view.copy_requested.connect(self._on_copy)
        self.view.algorithm_changed.connect(self._on_algorithm_changed)

        # 连接模型信号
        self.model.file_selected.connect(self.view.update_file_info)
        self.model.hash_calculated.connect(self._on_hash_calculated)
        self.model.progress_updated.connect(self.view.update_progress)
        self.model.error_occurred.connect(self._on_error)
        self.model.status_updated.connect(self.view.update_status)

        # 初始化状态
        self.view.update_status("就绪")
        self.view.enable_copy_button(False)

    def _on_file_selected(self, file_path: str):
        """文件被选择"""
        self.model.select_file(file_path)
        self.view.clear_result()
        self.view.enable_copy_button(False)

    def _on_browse_file(self):
        """浏览文件"""
        parent = self.view
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "选择要校验的文件",
            "",
            "所有文件 (*.*)"
        )
        if file_path:
            self._on_file_selected(file_path)

    def _on_calculate(self):
        """开始计算HASH"""
        self.view.set_calculating_state(True)
        self.view.enable_copy_button(False)
        self.model.calculate_hash()

    def _on_clear(self):
        """清空结果"""
        self.view.clear_result()
        self.view.enable_copy_button(False)
        self.view.update_status("已清空结果")

    def _on_copy(self):
        """复制HASH"""
        hash_text = self.view.get_hash_text()
        if hash_text and "HASH值:" in hash_text:
            # 提取HASH值
            lines = hash_text.split('\n')
            for line in lines:
                if 'HASH值:' in line:
                    hash_value = line.split('HASH值:')[1].strip()
                    # 获取系统剪贴板
                    clipboard = QApplication.clipboard()
                    clipboard.setText(hash_value)
                    self.view.update_status("HASH值已复制到剪贴板")
                    self.view.show_info("复制成功", "HASH值已复制到剪贴板")
                    return
        self.view.show_warning("警告", "没有可复制的内容")

    def _on_algorithm_changed(self, algorithm_name: str):
        """算法改变"""
        try:
            algorithm = HashAlgorithm(algorithm_name)
            self.model.set_algorithm(algorithm)
            self.view.update_status(f"已切换到 {algorithm_name} 算法")
        except ValueError:
            self.view.show_error(f"不支持的算法: {algorithm_name}")

    def _on_hash_calculated(self, algorithm: str, hash_value: str):
        """HASH计算完成"""
        self.view.show_hash_result(algorithm, hash_value)
        self.view.set_calculating_state(False)
        self.view.enable_copy_button(True)

    def _on_error(self, error: str):
        """错误处理"""
        self.view.show_error(error)
        self.view.set_calculating_state(False)
        self.view.enable_copy_button(False)
