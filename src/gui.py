import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QTcpSocket, QTcpServer, QHostAddress
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit
)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HTTP Proxy")
        self.setMinimumSize(800, 600)

        self.parent_widget = QWidget()
        self.parent_widget.setContentsMargins(0, 0, 0, 0)

        # Main Layout
        self.main_layout = QVBoxLayout()

        self.toolbar = Toolbar()

        self.content_view = QStackedLayout()
        self.blank_screen = BlankScreen(self)
        self.log_view = LogView(self)
        self.content_view.addWidget(self.blank_screen)
        self.content_view.addWidget(self.log_view)

        self.status_bar = StatusBar()

        self.main_layout.addLayout(self.toolbar)
        self.main_layout.addLayout(self.content_view)
        self.main_layout.addLayout(self.status_bar)

        self.parent_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.parent_widget)
        self.toolbar.start_btn.toggled.connect(self.handle_start_stop)

        # IO
        self.server = QTcpServer(self)
        self.sock: QTcpSocket | None = None
        self.start_internal_io_server()

    @Slot()
    def handle_start_stop(self, started):
        if started:
            self.content_view.setCurrentIndex(1)
            self.status_bar.status.setText(
                "Proxy running at "
                f"http://{self.toolbar.listen_host_input.text()}:{self.toolbar.listen_port_input.text()}."
            )
        else:
            self.content_view.setCurrentIndex(0)
            self.status_bar.status.setText(
                "Proxy is not running."
            )

    def start_internal_io_server(self):
        default_port = 54321
        self.server.setMaxPendingConnections(1)
        self.server.newConnection.connect(self.handle_inbound_conn)
        if not self.server.listen(QHostAddress.Any, default_port):
            self.status_bar.status.setText(
                "An error occurred while setting up the proxy, please restart."
            )

    @Slot()
    def handle_inbound_conn(self):
        self.sock = self.server.nextPendingConnection()
        if self.sock:
            self.sock.readyRead.connect(self.handle_rx)

    @Slot()
    def handle_rx(self):
        length = self.sock.bytesAvailable()
        # noinspection PyTypeChecker
        data = bytes(self.sock.read(length)).decode()
        self.log_view.insertPlainText(f"\n\n{'-'*10} [{datetime.now()}] {'-'*10}\n{data}")
        self.log_view.ensureCursorVisible()


class Toolbar(QVBoxLayout):
    def __init__(self):
        super().__init__()

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setEnabled(False)
        self.search_bar.setStyleSheet("padding: 8px")

        self.addWidget(self.search_bar)

        # Config Layout
        conf_layout = QHBoxLayout()
        self.listen_host_label = QLabel("Listen Host: ")
        self.listen_host_input = QLineEdit("127.0.0.1")
        self.listen_host_input.setEnabled(False)

        self.listen_port_label = QLabel("Listen Port: ")
        self.listen_port_input = QLineEdit("8080")
        self.listen_port_input.setEnabled(False)

        self.start_btn = QPushButton("Start")
        self.start_btn.setCheckable(True)
        self.start_btn.toggled.connect(self.handle_start_stop)

        conf_layout.addWidget(self.listen_host_label)
        conf_layout.addWidget(self.listen_host_input)
        conf_layout.addWidget(self.listen_port_label)
        conf_layout.addWidget(self.listen_port_input)
        conf_layout.addWidget(self.start_btn)

        self.addLayout(conf_layout)

    def handle_start_stop(self, started):
        if started:
            self.start_btn.setText("Stop")
            # self.listen_host_input.setEnabled(False)
            # self.listen_port_input.setEnabled(False)
            self.search_bar.setEnabled(True)
        else:
            self.start_btn.setText("Start")
            # self.listen_host_input.setEnabled(True)
            # self.listen_port_input.setEnabled(True)
            self.search_bar.setEnabled(False)


class BlankScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 120, 0, 120)

        logo = QLabel()
        logo.setPixmap(QPixmap(Path(__file__).parent.resolve() / "assets/logo.svg"))

        title = QLabel("Computer Networks (ARI 205)")
        title.setStyleSheet("font-size: 20px; color: #ddd; font-weight: bold")

        project_title = QLabel("Project: HTTP Proxy")
        project_title.setStyleSheet("font-size: 18px; font-weight: 500; color: #ccc")

        authors = QLabel(
            "Dhruv Grover (006), Pranav Bisht (027), Sujal Singh (041), Prashant Pulkit (045), Ocean Bhatnagar (063)"
        )
        authors.setStyleSheet("color: #ccc")

        for item in (logo, title, project_title, authors):
            if isinstance(item, QLabel):
                item.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(project_title)
        layout.addWidget(authors)

        self.setLayout(layout)


class LogView(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setReadOnly(True)


class StatusBar(QHBoxLayout):
    def __init__(self):
        super().__init__()

        self.status = QLabel("Proxy is not running.")
        self.status.setStyleSheet("color: #aaa")

        self.addWidget(self.status)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
