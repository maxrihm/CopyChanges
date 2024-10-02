from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QTabWidget, QSizePolicy, QSplitter
from views.text_editor import TextEditor
from views.file_browser import FileBrowser
from controllers.main_controller import MainController


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize tabs and layouts
        self.tabs = QTabWidget()  # Create a tab widget

        # Initialize the file browser first, then pass to the controller later
        self.file_browser = FileBrowser()

        # Initialize tab content but don't initialize the controller yet
        self.init_text_editor_tab()

        # Now initialize the controller after the editors and file_browser are ready
        self.controller = MainController(self)

        # Set the controller for the file browser
        self.file_browser.set_controller(self.controller.file_browser_controller)

        self.init_file_browser_tab()  # Initialize file browser after controller is available

        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        self.setLayout(main_layout)
        self.setWindowTitle('Advanced File and Prompt Line Editor with Tabs')
        self.setGeometry(300, 300, 1500, 900)

    def init_text_editor_tab(self):
        """Initialize the tab containing the nine text editors."""
        text_editor_tab = QWidget()
        layout = QGridLayout()

        self.editors = [TextEditor() for _ in range(9)]

        self.status_label = QLabel("")
        layout.addWidget(self.status_label, 0, 0, 1, 3)

        # Initialize the project_directory_label
        self.project_directory_label = QLabel("Project Directory: Not Set")
        layout.addWidget(self.project_directory_label, 1, 0, 1, 3)  # Ensure it's added to the layout

        for i in range(9):
            layout.addWidget(QLabel(f"Window {i + 1} (Editor {i + 1}):"), 4 + (i // 3) * 3, i % 3)
            layout.addWidget(self.editors[i], 5 + (i // 3) * 3, i % 3)
            copy_button = self.create_copy_button(self.editors[i], f"Read and Copy Content (Window {i + 1})",
                                                  f"Window {i + 1}")
            layout.addWidget(copy_button, 6 + (i // 3) * 3, i % 3)

        text_editor_tab.setLayout(layout)
        self.tabs.addTab(text_editor_tab, "Text Editors")

        # When this tab is clicked, load the workspace
        self.tabs.currentChanged.connect(self.on_tab_change)

    def init_file_browser_tab(self):
        """Initialize the tab containing the file browser and git changes."""
        file_browser_tab = QWidget()
        layout = QGridLayout()

        # File Browser and Git Buttons
        self.browse_button = QPushButton("Browse Project Directory")
        self.browse_button.clicked.connect(self.controller.browse_project_directory)
        self.browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.browse_button, 0, 0)

        self.git_button = QPushButton("Get Git Changes (Window 1)")
        self.git_button.clicked.connect(self.controller.get_git_changes)
        self.git_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.git_button, 1, 0)

        # Create a splitter to hold the file browser
        splitter = QSplitter()
        splitter.addWidget(self.file_browser)

        layout.addWidget(splitter, 2, 0, 1, 2)

        file_browser_tab.setLayout(layout)
        self.tabs.addTab(file_browser_tab, "File Browser & Git")

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

    def on_tab_change(self, index):
        """Handle actions when the user changes tabs."""
        if self.tabs.tabText(index) == "Text Editors":
            print("Text Editors tab selected, refreshing Window 1.")
            self.editors[0].repaint()
