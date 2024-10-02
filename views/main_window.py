# views/main_window.py

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QSizePolicy, QSplitter
from views.text_editor import TextEditor
from views.file_browser import FileBrowser
from controllers.main_controller import MainController


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.editors = [TextEditor() for _ in range(9)]
        self.controller = MainController(self)
        self.file_browser = self.controller.file_browser

        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        self.status_label = QLabel("")
        layout.addWidget(self.status_label, 0, 0, 1, 3)

        self.project_directory_label = QLabel("Project Directory:")
        layout.addWidget(self.project_directory_label, 1, 0, 1, 3)

        self.browse_button = QPushButton("Browse Project Directory")
        self.browse_button.clicked.connect(self.controller.browse_project_directory)
        self.browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.browse_button, 2, 0)

        self.git_button = QPushButton("Get Git Changes (Window 1)")
        self.git_button.clicked.connect(self.controller.get_git_changes)
        self.git_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.git_button, 3, 0)

        # Create a splitter to hold the file browser and the text editors
        splitter = QSplitter()
        splitter.addWidget(self.file_browser)

        editor_widget = QWidget()
        editor_layout = QGridLayout()

        for i in range(9):
            editor_layout.addWidget(QLabel(f"Window {i+1} (Editor {i+1}):"), 4 + (i//3)*3, i % 3)
            editor_layout.addWidget(self.editors[i], 5 + (i//3)*3, i % 3)
            copy_button = self.create_copy_button(self.editors[i], f"Read and Copy Content (Window {i+1})", f"Window {i+1}")
            editor_layout.addWidget(copy_button, 6 + (i//3)*3, i % 3)

        editor_widget.setLayout(editor_layout)
        splitter.addWidget(editor_widget)

        layout.addWidget(splitter, 4, 0, 1, 3)

        self.setLayout(layout)
        self.setWindowTitle('Advanced File and Prompt Line Editor')
        self.setGeometry(300, 300, 1500, 900)

        self.controller.load_last_workspace()

    def create_copy_button(self, editor, button_text, window_name):
        copy_button = QPushButton(button_text)
        copy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        copy_button.clicked.connect(lambda: self.controller.read_content(editor, window_name))
        return copy_button

    def update_status(self, message, error=False):
        if error:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: black;")
        self.status_label.setText(message)

    def update_project_directory_label(self, directory):
        self.project_directory_label.setText(f"Project Directory: {directory}")

    def closeEvent(self, event):
        self.controller.close_event()
        event.accept()
