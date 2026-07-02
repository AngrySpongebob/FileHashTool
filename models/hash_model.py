import hashlib
import os
from enum import Enum
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker


class HashAlgorithm(Enum):
    """支持的HASH算法枚举"""
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA224 = "SHA224"
    SHA256 = "SHA256"
    SHA384 = "SHA384"
    SHA512 = "SHA512"

    @classmethod
    def get_all_values(cls):
        return [algo.value for algo in cls]


class HashCalculator(QThread):
    """HASH计算线程"""
    progress_updated = Signal(int)  # 进度更新信号 (0-100)
    result_ready = Signal(str, str)  # 结果就绪信号 (算法名称, HASH值)
    error_occurred = Signal(str)  # 错误信号

    def __init__(self):
        super().__init__()
        self.file_path = None
        self.algorithm = HashAlgorithm.MD5
        self._is_running = False
        self._mutex = QMutex()

    def set_task(self, file_path: str, algorithm: HashAlgorithm):
        """设置计算任务"""
        with QMutexLocker(self._mutex):
            self.file_path = file_path
            self.algorithm = algorithm

    def stop(self):
        """停止计算"""
        with QMutexLocker(self._mutex):
            self._is_running = False

    def run(self):
        """执行HASH计算"""
        with QMutexLocker(self._mutex):
            if not self.file_path or not os.path.exists(self.file_path):
                self.error_occurred.emit("文件不存在")
                return

            self._is_running = True

        try:
            # 获取对应的HASH算法
            algo_name = self.algorithm.value.lower()
            hash_func = getattr(hashlib, algo_name, None)
            if not hash_func:
                self.error_occurred.emit(f"不支持的HASH算法: {algo_name}")
                return

            hasher = hash_func()
            file_size = os.path.getsize(self.file_path)
            processed = 0
            buffer_size = 8192

            with open(self.file_path, 'rb') as f:
                while self._is_running:
                    data = f.read(buffer_size)
                    if not data:
                        break
                    hasher.update(data)
                    processed += len(data)
                    progress = int((processed / file_size) * 100)
                    self.progress_updated.emit(progress)

            if not self._is_running:
                return

            hash_value = hasher.hexdigest()
            self.result_ready.emit(self.algorithm.value, hash_value)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def is_running(self):
        """检查是否正在运行"""
        with QMutexLocker(self._mutex):
            return self._is_running


class HashModel(QObject):
    """HASH校验模型"""
    # 信号
    file_selected = Signal(dict)  # 文件选择信号
    hash_calculated = Signal(str, str)  # HASH计算完成信号 (算法, HASH值)
    progress_updated = Signal(int)  # 进度更新信号
    error_occurred = Signal(str)  # 错误信号
    status_updated = Signal(str)  # 状态更新信号

    def __init__(self):
        super().__init__()
        self._current_file = None
        self._algorithm = HashAlgorithm.SHA256
        self._calculator = None
        self._last_hash_result = None

    def set_algorithm(self, algorithm: HashAlgorithm):
        """设置当前算法"""
        self._algorithm = algorithm

    def get_algorithm(self) -> HashAlgorithm:
        """获取当前算法"""
        return self._algorithm

    def select_file(self, file_path: str) -> bool:
        """选择文件"""
        from utils.file_utils import FileUtils

        if not os.path.exists(file_path):
            self.error_occurred.emit("文件不存在")
            return False

        file_info = FileUtils.get_file_info(file_path)
        if file_info:
            self._current_file = file_path
            self.file_selected.emit(file_info)
            self.status_updated.emit(f"已选择文件: {file_info['name']}")
            return True
        return False

    def calculate_hash(self):
        """开始计算HASH"""
        if not self._current_file:
            self.error_occurred.emit("请先选择文件")
            return

        if self._calculator and self._calculator.is_running():
            self.error_occurred.emit("正在计算中，请稍候...")
            return

        # 创建计算线程
        self._calculator = HashCalculator()
        self._calculator.set_task(self._current_file, self._algorithm)

        # 连接信号
        self._calculator.progress_updated.connect(self._on_progress_updated)
        self._calculator.result_ready.connect(self._on_hash_result)
        self._calculator.error_occurred.connect(self._on_calculation_error)
        self._calculator.finished.connect(self._on_calculation_finished)

        self.status_updated.emit(f"正在计算 {self._algorithm.value} HASH...")
        self._calculator.start()

    def _on_progress_updated(self, progress: int):
        """处理进度更新"""
        self.progress_updated.emit(progress)
        self.status_updated.emit(f"计算中... {progress}%")

    def _on_hash_result(self, algorithm: str, hash_value: str):
        """处理HASH结果"""
        self._last_hash_result = hash_value
        self.hash_calculated.emit(algorithm, hash_value)
        self.status_updated.emit(f"计算完成 - {algorithm}")
        self.progress_updated.emit(100)

    def _on_calculation_error(self, error: str):
        """处理计算错误"""
        self.error_occurred.emit(error)
        self.status_updated.emit(f"错误: {error}")

    def _on_calculation_finished(self):
        """计算完成清理"""
        if self._calculator:
            self._calculator.deleteLater()
            self._calculator = None

    def get_last_hash(self) -> str:
        """获取最后一次计算的HASH值"""
        return self._last_hash_result

    def cancel_calculation(self):
        """取消计算"""
        if self._calculator and self._calculator.is_running():
            self._calculator.stop()
            self.status_updated.emit("已取消计算")