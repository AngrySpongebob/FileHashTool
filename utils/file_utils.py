import os
from datetime import datetime


class FileUtils:
    """文件工具类"""

    @staticmethod
    def format_file_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    @staticmethod
    def get_file_info(file_path: str) -> dict[str, str | int] | None:
        """获取文件信息"""
        if not os.path.exists(file_path):
            return None

        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_formatted': FileUtils.format_file_size(stat.st_size),
            'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'path': file_path
        }
