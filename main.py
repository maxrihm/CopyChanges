import sys
import os
import subprocess
import json
import pyperclip
from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit, QVBoxLayout, QLabel, QPushButton, QFileDialog, \
    QHBoxLayout, QTextEdit
from PyQt5.QtGui import QColor, QPainter, QTextOption
from PyQt5.QtCore import Qt, QRect, QSize


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class TextEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)  # Enable word wrap

    def line_number_area_width(self):
        digits = len(str(self.blockCount()))
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(line_color)
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.line_number_area.width(), self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.project_directory = ""
        self.save_file = "textboxes_content.json"

        # Create three text editors
        self.editor1 = TextEditor()  # First window/editor
        self.editor2 = TextEditor()  # Second window/editor
        self.editor3 = TextEditor()  # Third window/editor

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label for showing prompt/file line count
        self.status_label = QLabel("Prompt lines: 0 | File lines: 0")
        layout.addWidget(self.status_label)

        # Project directory input section
        self.project_directory_label = QLabel("Project Directory:")
        layout.addWidget(self.project_directory_label)

        self.browse_button = QPushButton("Browse Project Directory")
        self.browse_button.clicked.connect(self.browse_project_directory)
        layout.addWidget(self.browse_button)

        # Buttons and Text Editors layout
        buttons_layout = QHBoxLayout()

        # Git Changes button (only for first window)
        self.git_button = QPushButton("Get Git Changes (Window 1)")
        self.git_button.clicked.connect(self.get_git_changes)
        buttons_layout.addWidget(self.git_button)

        # Add all three text editors to the layout with their respective "Read and Copy Content" buttons
        layout.addLayout(buttons_layout)

        layout.addWidget(QLabel("Window 1 (Editor 1):"))
        layout.addWidget(self.editor1)
        layout.addWidget(self.create_copy_button(self.editor1, "Read and Copy Content (Window 1)"))

        layout.addWidget(QLabel("Window 2 (Editor 2):"))
        layout.addWidget(self.editor2)
        layout.addWidget(self.create_copy_button(self.editor2, "Read and Copy Content (Window 2)"))

        layout.addWidget(QLabel("Window 3 (Editor 3):"))
        layout.addWidget(self.editor3)
        layout.addWidget(self.create_copy_button(self.editor3, "Read and Copy Content (Window 3)"))

        self.setLayout(layout)
        self.setWindowTitle('Advanced File and Prompt Line Editor')
        self.setGeometry(300, 300, 600, 900)  # Adjusted height for three windows

        # Load saved content
        self.load_content()

    def create_copy_button(self, editor, button_text):
        """ Helper function to create a button for copying content """
        copy_button = QPushButton(button_text)
        copy_button.clicked.connect(lambda: self.read_content(editor))
        return copy_button

    def browse_project_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.project_directory = directory
            self.project_directory_label.setText(f"Project Directory: {self.project_directory}")
            self.save_content()

    def get_git_changes(self):
        if not self.project_directory:
            self.show_error("Please set a valid project directory first.")
            return

        try:
            os.chdir(self.project_directory)
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            changed_files = result.stdout.splitlines()
            file_paths = [file[3:] for file in changed_files if len(file) > 3]

            self.editor1.clear()
            for path in file_paths:
                self.editor1.appendPlainText(path)
        except Exception as e:
            self.show_error(f"Failed to get Git changes: {e}")

    def read_content(self, editor):
        prompt_lines_count = 0
        file_lines_count = 0
        content = ""
        file_paths = editor.toPlainText().splitlines()

        for file_path in file_paths:
            file_path = file_path.strip()
            full_path = os.path.join(self.project_directory, file_path)

            if os.path.isfile(full_path):
                # Treat it as a file line
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content += f"Content of {file_path}:\n{f.read()}\n{'-' * 80}\n"
                        file_lines_count += 1
                except Exception as e:
                    content += f"Failed to read {file_path}: {e}\n"
            elif file_path == "":
                # Empty line, treat it as a line break
                content += "\n"
            else:
                # Treat as a prompt line
                prompt_lines_count += 1
                content += f"{file_path}\n"

        pyperclip.copy(content)
        self.status_label.setText(f"Prompt lines: {prompt_lines_count} | File lines: {file_lines_count}")
        self.show_message(f"Content copied to clipboard.\nPrompt lines: {prompt_lines_count}\nFile lines: {file_lines_count}")

    def show_message(self, message):
        msg = QLabel(message)
        msg.show()

    def show_error(self, message):
        msg = QLabel(message)
        msg.show()

    def save_content(self):
        data = {
            "project_directory": self.project_directory,
            "editor1_content": self.editor1.toPlainText(),
            "editor2_content": self.editor2.toPlainText(),
            "editor3_content": self.editor3.toPlainText(),
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f)

    def load_content(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.project_directory = data.get("project_directory", "")
                self.project_directory_label.setText(f"Project Directory: {self.project_directory}")
                self.editor1.setPlainText(data.get("editor1_content", ""))
                self.editor2.setPlainText(data.get("editor2_content", ""))
                self.editor3.setPlainText(data.get("editor3_content", ""))

    def closeEvent(self, event):
        self.save_content()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
