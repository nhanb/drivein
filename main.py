import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from google import (
    build_oauth_url,
    get_initial_tokens,
    wait_for_authorization_code,
)
from rclone import kill, mount, rclone_is_running, write_config


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("DriveIn")

        layout = QVBoxLayout()
        self.init_authorize_button(layout)
        self.init_rclone_buttons(layout)

        widget = QWidget()
        widget.setLayout(layout)
        widget.width = 400

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    def init_authorize_button(self, layout):
        authorizeBtn = QPushButton("Authorize DriveIn")
        authorizeBtn.clicked.connect(self.onAuthorizeBtnClicked)
        self.authorizeBtn = authorizeBtn

        layout.addWidget(QLabel("Step 1:"))
        layout.addWidget(authorizeBtn)

    def init_rclone_buttons(self, layout):
        mountBtn = QPushButton("Mount Google Drive")
        mountBtn.clicked.connect(self.onMountBtnClicked)
        self.mountBtn = mountBtn

        unmountBtn = QPushButton("Unmount Google Drive")
        unmountBtn.clicked.connect(self.onUnmountBtnClicked)
        self.unmountBtn = unmountBtn

        layout.addWidget(QLabel("Step 2:"))
        layout.addWidget(mountBtn)

        layout.addWidget(QLabel("Step 3 (optional):"))
        layout.addWidget(unmountBtn)

        if rclone_is_running():
            mountBtn.setEnabled(False)
        else:
            unmountBtn.setEnabled(False)

    def onAuthorizeBtnClicked(self, _):
        handler = wait_for_authorization_code()
        redirect_port = next(handler)
        oauth_url = build_oauth_url(redirect_port)

        QDesktopServices.openUrl(QUrl(oauth_url))

        authorization_code = next(handler)
        tokens = get_initial_tokens(authorization_code, redirect_port)

        write_config(tokens["refresh_token"])
        self.authorizeBtn.setDisabled(True)
        self.authorizeBtn.setText("You're now authorized.")

    def onMountBtnClicked(self, _):
        self.mount()

    def onUnmountBtnClicked(self, _):
        self.unmount()

    def unmount(self):
        kill()
        self.mountBtn.setEnabled(True)
        self.unmountBtn.setEnabled(False)

    def mount(self):
        mount(shell=False)
        self.mountBtn.setEnabled(False)
        self.unmountBtn.setEnabled(True)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
