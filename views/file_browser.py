# views/file_browser.py

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton
import os


class FileBrowser(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File/Folder Structure"])
        layout.addWidget(self.tree)

        self.get_files_button = QPushButton("Get Files")
        self.get_files_button.clicked.connect(self.controller.get_selected_files)
        layout.addWidget(self.get_files_button)

        self.setLayout(layout)

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
