import sys
import os
import subprocess
import json
import pyperclip
from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit, QVBoxLayout, QLabel, QPushButton, QFileDialog, \
    QHBoxLayout, QGridLayout, QSizePolicy, QTextEdit
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

        self.editor1 = TextEditor()
        self.editor2 = TextEditor()
        self.editor3 = TextEditor()
        self.editor4 = TextEditor()
        self.editor5 = TextEditor()
        self.editor6 = TextEditor()
        self.editor7 = TextEditor()
        self.editor8 = TextEditor()
        self.editor9 = TextEditor()

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

        layout.addWidget(QLabel("Window 1 (Editor 1):"), 4, 0)
        layout.addWidget(self.editor1, 5, 0)
        layout.addWidget(self.create_copy_button(self.editor1, "Read and Copy Content (Window 1)", "Window 1"), 6, 0)

        layout.addWidget(QLabel("Window 2 (Editor 2):"), 7, 0)
        layout.addWidget(self.editor2, 8, 0)
        layout.addWidget(self.create_copy_button(self.editor2, "Read and Copy Content (Window 2)", "Window 2"), 9, 0)

        layout.addWidget(QLabel("Window 3 (Editor 3):"), 10, 0)
        layout.addWidget(self.editor3, 11, 0)
        layout.addWidget(self.create_copy_button(self.editor3, "Read and Copy Content (Window 3)", "Window 3"), 12, 0)

        layout.addWidget(QLabel("Window 4 (Editor 4):"), 4, 1)
        layout.addWidget(self.editor4, 5, 1)
        layout.addWidget(self.create_copy_button(self.editor4, "Read and Copy Content (Window 4)", "Window 4"), 6, 1)

        layout.addWidget(QLabel("Window 5 (Editor 5):"), 7, 1)
        layout.addWidget(self.editor5, 8, 1)
        layout.addWidget(self.create_copy_button(self.editor5, "Read and Copy Content (Window 5)", "Window 5"), 9, 1)

        layout.addWidget(QLabel("Window 6 (Editor 6):"), 10, 1)
        layout.addWidget(self.editor6, 11, 1)
        layout.addWidget(self.create_copy_button(self.editor6, "Read and Copy Content (Window 6)", "Window 6"), 12, 1)

        layout.addWidget(QLabel("Window 7 (Editor 7):"), 4, 2)
        layout.addWidget(self.editor7, 5, 2)
        layout.addWidget(self.create_copy_button(self.editor7, "Read and Copy Content (Window 7)", "Window 7"), 6, 2)

        layout.addWidget(QLabel("Window 8 (Editor 8):"), 7, 2)
        layout.addWidget(self.editor8, 8, 2)
        layout.addWidget(self.create_copy_button(self.editor8, "Read and Copy Content (Window 8)", "Window 8"), 9, 2)

        layout.addWidget(QLabel("Window 9 (Editor 9):"), 10, 2)
        layout.addWidget(self.editor9, 11, 2)
        layout.addWidget(self.create_copy_button(self.editor9, "Read and Copy Content (Window 9)", "Window 9"), 12, 2)

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

            self.editor1.clear()
            for path in file_paths:
                self.editor1.appendPlainText(path)
        except Exception as e:
            self.update_status(f"Failed to get Git changes: {e}", error=True)

    def read_content(self, editor, window_name):
        prompt_lines_count = 0
        file_lines_count = 0
        line_breaks_count = 0
        window_lines_count = 0  # This will count how many lines are window references
        content = ""
        file_paths = editor.toPlainText().splitlines()

        for file_path in file_paths:
            file_path = file_path.strip()

            if file_path and file_path[0].isdigit():
                window_number = int(file_path[0])
                if 1 <= window_number <= 9:
                    window_lines_count += 1
                    content += self.read_nested_window_content(window_number) + "\n"
                    continue

            full_path = os.path.join(self.project_directory, file_path)

            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content += f"Content of {file_path}:\n{f.read()}\n\n\n"
                        file_lines_count += 1
                except Exception as e:
                    content += f"Failed to read {file_path}: {e}\n"
            elif file_path == "":
                content += "\n"
                line_breaks_count += 1
            else:
                prompt_lines_count += 1
                content += f"{file_path}\n"

        if file_paths and file_paths[-1].strip() == "":
            line_breaks_count += 1

        content = self.replace_placeholders(content)
        pyperclip.copy(content)
        self.update_status(
            f"Copied from {window_name} | Prompt lines: {prompt_lines_count} | File lines: {file_lines_count} | Line breaks: {line_breaks_count} | Window lines: {window_lines_count}")

    def read_nested_window_content(self, window_number):
        editor = getattr(self, f'editor{window_number}')
        content = editor.toPlainText().splitlines()

        result = ""
        for line in content:
            line = line.strip()

            if line and line[0].isdigit():
                nested_window_number = int(line[0])
                if 1 <= nested_window_number <= 9:
                    result += self.read_nested_window_content(nested_window_number) + "\n"
            else:
                full_path = os.path.join(self.project_directory, line)
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            result += f"Content of {line}:\n{f.read()}\n\n\n"
                    except Exception as e:
                        result += f"Failed to read {line}: {e}\n"
                else:
                    result += line + "\n"

        return result

    def replace_placeholders(self, content):
        for i in range(1, 10):
            content = content.replace(f'[{i}]', getattr(self, f'editor{i}').toPlainText())
        return content

    def update_status(self, message, error=False):
        if error:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: black;")
        self.status_label.setText(message)

    def save_content(self):
        data = {}
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)

        data[self.project_directory] = {
            "editor1_content": self.editor1.toPlainText(),
            "editor2_content": self.editor2.toPlainText(),
            "editor3_content": self.editor3.toPlainText(),
            "editor4_content": self.editor4.toPlainText(),
            "editor5_content": self.editor5.toPlainText(),
            "editor6_content": self.editor6.toPlainText(),
            "editor7_content": self.editor7.toPlainText(),
            "editor8_content": self.editor8.toPlainText(),
            "editor9_content": self.editor9.toPlainText(),
        }

        data["last_project_directory"] = self.project_directory  # Save last used project directory
        with open(self.save_file, "w") as f:
            json.dump(data, f)

    def load_content(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                if self.project_directory in data:
                    content = data[self.project_directory]
                    self.editor1.setPlainText(content.get("editor1_content", ""))
                    self.editor2.setPlainText(content.get("editor2_content", ""))
                    self.editor3.setPlainText(content.get("editor3_content", ""))
                    self.editor4.setPlainText(content.get("editor4_content", ""))
                    self.editor5.setPlainText(content.get("editor5_content", ""))
                    self.editor6.setPlainText(content.get("editor6_content", ""))
                    self.editor7.setPlainText(content.get("editor7_content", ""))
                    self.editor8.setPlainText(content.get("editor8_content", ""))
                    self.editor9.setPlainText(content.get("editor9_content", ""))

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
