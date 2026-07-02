# -*- coding: utf-8 -*-
import sys
import os

from PySide6.QtGui import QIcon

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from models.hash_model import HashModel
from views.main_window import MainWindow
from controllers.hash_controller import HashController


def main():
    """程序入口"""
    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.ico"))
    app.setApplicationName("文件HASH校验工具")
    app.setOrganizationName("FileHashChecker")

    # 创建MVC组件
    model = HashModel()
    view = MainWindow()
    controller = HashController(model, view)

    # 保存到app属性以防止被垃圾回收
    app.controller = controller

    # 显示主窗口
    view.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
