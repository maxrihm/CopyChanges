import sys
import os
import subprocess
import json
import pyperclip
from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit, QLabel, QPushButton, QFileDialog, QGridLayout, \
    QSizePolicy, QTextEdit
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
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

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

        self.script_directory = os.path.dirname(os.path.abspath(__file__))
        self.save_file = os.path.join(self.script_directory, "textboxes_content.json")
        self.project_directory = ""

        self.editors = [TextEditor() for _ in range(9)]

        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        self.status_label = QLabel("Prompt lines: 0 | File lines: 0 | Line breaks: 0 | Window lines: 0")
        layout.addWidget(self.status_label, 0, 0, 1, 3)

        self.project_directory_label = QLabel("Project Directory:")
        layout.addWidget(self.project_directory_label, 1, 0, 1, 3)

        self.browse_button = QPushButton("Browse Project Directory")
        self.browse_button.clicked.connect(self.browse_project_directory)
        self.browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.browse_button, 2, 0)

        self.git_button = QPushButton("Get Git Changes (Window 1)")
        self.git_button.clicked.connect(self.get_git_changes)
        self.git_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.git_button, 3, 0)

        for i in range(9):
            layout.addWidget(QLabel(f"Window {i+1} (Editor {i+1}):"), 4 + (i//3)*3, i % 3)
            layout.addWidget(self.editors[i], 5 + (i//3)*3, i % 3)
            layout.addWidget(self.create_copy_button(self.editors[i], f"Read and Copy Content (Window {i+1})", f"Window {i+1}"), 6 + (i//3)*3, i % 3)

        self.setLayout(layout)
        self.setWindowTitle('Advanced File and Prompt Line Editor')
        self.setGeometry(300, 300, 1500, 900)
        self.load_last_workspace()

    def create_copy_button(self, editor, button_text, window_name):
        copy_button = QPushButton(button_text)
        copy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        copy_button.clicked.connect(lambda: self.read_content(editor, window_name))
        return copy_button

    def browse_project_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.project_directory = directory
            self.project_directory_label.setText(f"Project Directory: {self.project_directory}")
            self.save_content()

    def get_git_changes(self):
        if not self.project_directory:
            self.update_status("Please set a valid project directory first.", error=True)
            return

        try:
            os.chdir(self.project_directory)
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            changed_files = result.stdout.splitlines()
            file_paths = [file[3:] for file in changed_files if len(file) > 3]

            self.editors[0].clear()
            for path in file_paths:
                self.editors[0].appendPlainText(path)
        except Exception as e:
            self.update_status(f"Failed to get Git changes: {e}", error=True)

    def read_content(self, editor, window_name):
        content = ""
        lines = editor.toPlainText().splitlines()
        for line in lines:
            line = line.strip()
            content += self.process_line(line) + "\n"

        pyperclip.copy(content)
        self.update_status(f"Copied from {window_name}")

    def process_line(self, line):
        if not line:
            return ""
        if line[0].isdigit():  # Nested window reference
            return self.read_nested_window_content(int(line[0]))
        elif line.startswith('V'):  # Handle V syntax
            return self.handle_v_syntax(line[1:].strip())
        else:
            return self.read_file_content(line)

    def handle_v_syntax(self, json_path):
        json_data = self.load_json_data()
        if isinstance(json_data, str):  # Error in loading JSON
            return json_data

        normalized_json_path = json_path.lower().replace("/", "\\")
        result = ""
        for file_path, file_data in json_data.items():
            if normalized_json_path in file_path.lower():
                file_name = os.path.basename(file_path)
                result += f"Partial content of file {file_name}:\n"
                for item in file_data:
                    result += item['content'] + "\n...\n"
        if not result:
            return f"JSON path {json_path} not found."
        return result

    def read_nested_window_content(self, window_number):
        if 1 <= window_number <= 9:
            editor = self.editors[window_number - 1]
            return "\n".join(self.process_line(line.strip()) for line in editor.toPlainText().splitlines())
        return ""

    def read_file_content(self, file_path):
        full_path = os.path.join(self.project_directory, file_path)

        # If the file exists, read its content.
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f"Content of {os.path.basename(full_path)}:\n{f.read()}\n"
            except Exception as e:
                return f"Failed to read {file_path}: {e}\n"

        # If the file doesn't exist, return the original input line as regular text.
        return file_path

    def load_json_data(self):
        json_path = r"C:\Users\morge\copy-select\selections.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return f"Error loading JSON: {e}"

    def update_status(self, message, error=False):
        if error:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: black;")
        self.status_label.setText(message)

    def save_content(self):
        data = {self.project_directory: {f"editor{i+1}_content": editor.toPlainText() for i, editor in enumerate(self.editors)}}
        data["last_project_directory"] = self.project_directory
        with open(self.save_file, "w") as f:
            json.dump(data, f)

    def load_content(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                if self.project_directory in data:
                    content = data[self.project_directory]
                    for i, editor in enumerate(self.editors):
                        editor.setPlainText(content.get(f"editor{i+1}_content", ""))

    def load_last_workspace(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.project_directory = data.get("last_project_directory", "")
                if self.project_directory:
                    self.project_directory_label.setText(f"Project Directory: {self.project_directory}")
                    self.load_content()

    def closeEvent(self, event):
        self.save_content()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
