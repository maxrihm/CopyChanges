from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton
import os

class FileBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = None  # This will be set later
        self.init_ui()

    def set_controller(self, controller):
        """Allows the controller to be set after initialization."""
        self.controller = controller

    def init_ui(self):
        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File/Folder Structure"])
        layout.addWidget(self.tree)

        self.refresh_button = QPushButton("Refresh")
        layout.addWidget(self.refresh_button)

        self.get_files_button = QPushButton("Get Files")
        layout.addWidget(self.get_files_button)

        self.setLayout(layout)

        # Signals will be connected to the controller once it's set
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        self.get_files_button.clicked.connect(self._on_get_files_clicked)

    def _on_refresh_clicked(self):
        if self.controller:
            self.controller.refresh()

    def _on_get_files_clicked(self):
        if self.controller:
            self.controller.handle_file_selection()

    def load_directory(self, directory):
        self.tree.clear()
        self.add_items(self.tree.invisibleRootItem(), directory)

    def add_items(self, parent, path):
        for item_name in sorted(os.listdir(path)):
            full_path = os.path.join(path, item_name)
            tree_item = QTreeWidgetItem([item_name])
            tree_item.setCheckState(0, 0)
            parent.addChild(tree_item)

            if os.path.isdir(full_path):
                self.add_items(tree_item, full_path)

    def get_checked_items(self):
        checked_items = []
        root = self.tree.invisibleRootItem()
        self.get_checked_recursive(root, "", checked_items)
        return checked_items

    def get_checked_recursive(self, tree_item, current_path, checked_items):
        for i in range(tree_item.childCount()):
            child = tree_item.child(i)
            path = os.path.join(current_path, child.text(0))

            if child.checkState(0):
                checked_items.append(path)

            if child.childCount() > 0:
                self.get_checked_recursive(child, path, checked_items)

    def get_all_files(self):
        all_files = []
        root = self.tree.invisibleRootItem()
        self.get_all_files_recursive(root, "", all_files)
        return all_files

    def get_all_files_recursive(self, tree_item, current_path, all_files):
        for i in range(tree_item.childCount()):
            child = tree_item.child(i)
            path = os.path.join(current_path, child.text(0))
            all_files.append(path)

            if child.childCount() > 0:
                self.get_all_files_recursive(child, path, all_files)

    def refresh_checked_items(self, checked_files):
        root = self.tree.invisibleRootItem()
        self.refresh_checked_recursive(root, "", checked_files)

    def refresh_checked_recursive(self, tree_item, current_path, checked_files):
        for i in range(tree_item.childCount()):
            child = tree_item.child(i)
            path = os.path.join(current_path, child.text(0))

            if path in checked_files:
                child.setCheckState(0, 2)  # Check the item
            else:
                child.setCheckState(0, 0)  # Uncheck the item

            if child.childCount() > 0:
                self.refresh_checked_recursive(child, path, checked_files)
