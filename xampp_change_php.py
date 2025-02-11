import os
import shutil
import subprocess
import sys
import json
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox,
    QMessageBox, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import QThread, pyqtSignal

# XAMPPのインストールディレクトリ
XAMPP_PATH = "C:\\xampp"
PHP_PATH = os.path.join(XAMPP_PATH, "php")
APACHE_PATH = os.path.join(XAMPP_PATH, "apache")

def detect_current_version():
    """ 現在のシンボリックリンクの参照先を取得 """
    def resolve_symlink(path):
        if os.path.islink(path):
            return os.readlink(path)
        return "不明"

    return {
        "php": resolve_symlink(PHP_PATH),
        "apache": resolve_symlink(APACHE_PATH),
    }

def load_config():
    """ XAMPPフォルダをスキャンし、利用可能なバージョンを取得 """
    versions = {}
    for item in os.listdir(XAMPP_PATH):
        if item.startswith("php") and item[3:].replace(".", "").isdigit():  # php7.4, php8.1 形式
            version = item[3:]  # 'php7.4' -> '7.4'
            apache_folder = f"apache{version}"
            php_folder = os.path.join(XAMPP_PATH, item)

            if os.path.exists(os.path.join(XAMPP_PATH, apache_folder)):
                versions[version] = {
                    "php": php_folder,
                    "apache": os.path.join(XAMPP_PATH, apache_folder),
                }
    return versions

class SwitchThread(QThread):
    """ バックグラウンドでApacheの停止・再起動を実行するスレッド """
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    def run(self):
        self.log_signal.emit("Apache を停止中...")
        subprocess.run([os.path.join(XAMPP_PATH, "xampp_stop.exe")], shell=True)

        self.log_signal.emit("シンボリックリンクを変更中...")
        self.switch_symlink(PHP_PATH, self.paths["php"])
        self.switch_symlink(APACHE_PATH, self.paths["apache"])

        self.log_signal.emit("Apache を再起動中...")
        subprocess.run([os.path.join(XAMPP_PATH, "xampp_start.exe")], shell=True)

        self.log_signal.emit("切り替えが完了しました！")
        self.finished_signal.emit()

    def switch_symlink(self, target_path, new_path):
        """ シンボリックリンクを切り替える """
        if not new_path:
            return
        if os.path.exists(target_path):
            if os.path.islink(target_path):
                os.unlink(target_path)
            else:
                shutil.move(target_path, target_path + "_backup")
        os.symlink(new_path, target_path, target_is_directory=True)

class XAMPPVersionSwitcher(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("XAMPP バージョン管理ツール")
        self.setGeometry(100, 100, 600, 400)

        self.current_versions = detect_current_version()
        self.config = load_config()

        # 現在のバージョン表示
        self.current_label = QLabel(self.get_current_version_text())

        self.php_label = QLabel("切り替えるPHPのバージョンを選択:", self)
        self.php_combo = QComboBox(self)
        self.php_combo.addItems(self.config.keys())

        # ログ表示エリア
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.append("ログ: ")

        # ボタン
        self.switch_button = QPushButton("切り替え", self)
        self.switch_button.clicked.connect(self.switch_versions)

        self.reload_button = QPushButton("再読み込み", self)
        self.reload_button.clicked.connect(self.reload_versions)

        self.exit_button = QPushButton("終了", self)
        self.exit_button.clicked.connect(self.close)

        # レイアウト
        layout = QVBoxLayout()
        layout.addWidget(self.current_label)
        layout.addWidget(self.php_label)
        layout.addWidget(self.php_combo)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.switch_button)
        button_layout.addWidget(self.reload_button)
        layout.addLayout(button_layout)

        layout.addWidget(self.log_output)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

        self.switch_thread = None

    def get_current_version_text(self):
        """ 現在のバージョンを表示するテキストを作成 """
        return (f"現在のバージョン:\n"
                f"PHP: {self.get_version_from_path(self.current_versions['php'])}\n"
                f"Apache: {self.get_version_from_path(self.current_versions['apache'])}")

    def get_version_from_path(self, path):
        """ フォルダ名からバージョン番号を抽出 """
        if path == "不明":
            return "不明"
        return path.split("\\")[-1].replace("php", "").replace("apache", "")

    def reload_versions(self):
        """ バージョン情報を再読み込み """
        self.config = load_config()
        self.php_combo.clear()
        self.php_combo.addItems(self.config.keys())

        self.current_versions = detect_current_version()
        self.current_label.setText(self.get_current_version_text())
        self.log_output.append("バージョン情報を再読み込みしました。")

    def switch_versions(self):
        """ PHP, Apache, phpMyAdmin をバックグラウンドで切り替える """
        version = self.php_combo.currentText()
        if version not in self.config:
            QMessageBox.critical(self, "エラー", "選択したバージョンが見つかりません。")
            return

        paths = self.config[version]
        self.log_output.append(f"切り替え開始: PHP {version}, Apache {version}")

        # スレッドを作成して切り替えを非同期で実行
        self.switch_thread = SwitchThread(paths)
        self.switch_thread.log_signal.connect(self.log_output.append)
        self.switch_thread.finished_signal.connect(self.on_switch_finished)
        self.switch_thread.start()

    def on_switch_finished(self):
        """ 切り替え完了後の処理 """
        self.current_versions = detect_current_version()
        self.current_label.setText(self.get_current_version_text())
        QMessageBox.information(self, "成功", "バージョンの切り替えが完了しました！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XAMPPVersionSwitcher()
    window.show()
    sys.exit(app.exec())
