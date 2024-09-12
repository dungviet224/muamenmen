import sys
import os
import subprocess
import time
from threading import Thread
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
                             QLineEdit, QProgressBar, QLabel)

# Hàm để cài đặt pip nếu chưa có
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Danh sách các thư viện cần cài đặt
libraries = [
    "pandas",
    "selenium",
    "PyQt5",
    "Pillow",
    "pyperclip",
    "pywin32"
]

# Cài đặt từng thư viện
for lib in libraries:
    install(lib)

class GitHubDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.thread = None
        self.is_running = False

    def initUI(self):
        self.setWindowTitle("GitHub File Downloader")
        layout = QVBoxLayout()

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter GitHub file URL")
        layout.addWidget(self.url_input)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_download)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_download)
        layout.addWidget(self.stop_button)

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.time_left_label = QLabel("Time left: N/A")
        layout.addWidget(self.time_left_label)

        self.setLayout(layout)

    def start_download(self):
        if not self.is_running:
            self.is_running = True
            self.progress.setValue(0)
            self.log_output.append("Starting download...")
            self.thread = Thread(target=self.download_files)
            self.thread.start()

    def stop_download(self):
        self.is_running = False
        self.log_output.append("Download stopped.")

    def download_files(self):
        # Giả lập quá trình tải file
        total_files = 10  # Giả sử có 10 file cần tải
        for i in range(total_files):
            if not self.is_running:
                break
            # Giả lập kiểm tra file và sửa lỗi nếu cần
            time.sleep(1)  # Giả lập thời gian tải file
            self.progress.setValue((i + 1) * 10)
            self.log_output.append(f"Downloaded file {i + 1}")

            # Cập nhật thời gian còn lại
            time_left = (total_files - (i + 1)) * 1  # Giả lập 1 giây cho mỗi file
            self.time_left_label.setText(f"Time left: {time_left} seconds")

        if self.is_running:
            self.log_output.append("Download complete.")
        self.is_running = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = GitHubDownloader()
    downloader.resize(400, 300)
    downloader.show()
    sys.exit(app.exec_())
