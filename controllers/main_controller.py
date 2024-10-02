# controllers/main_controller.py

import os
import json
import pyperclip
from PyQt5.QtWidgets import QFileDialog

from utils.file_utils import read_file_content
from utils.json_utils import load_json_file
from utils.git_utils import get_git_changes
import config


class MainController:
    def __init__(self, view):
        self.view = view
        self.project_directory = ""
        self.editors = view.editors
        self.save_file = config.SAVE_FILE

    def browse_project_directory(self):
        directory = QFileDialog.getExistingDirectory(self.view, "Select Project Directory")
        if directory:
            self.project_directory = directory
            self.view.update_project_directory_label(self.project_directory)
            self.save_content()

    def get_git_changes(self):
        if not self.project_directory:
            self.view.update_status("Please set a valid project directory first.", error=True)
            return

        file_paths = get_git_changes(self.project_directory)
        if isinstance(file_paths, str):
            self.view.update_status(file_paths, error=True)
            return

        self.editors[0].clear()
        for path in file_paths:
            self.editors[0].appendPlainText(path)

    def read_content(self, editor, window_name):
        content = ""
        lines = editor.toPlainText().splitlines()
        for line in lines:
            line = line.strip()
            content += self.process_line(line) + "\n"

        pyperclip.copy(content)
        self.view.update_status(f"Copied from {window_name}")

    def process_line(self, line):
        if not line:
            return ""
        if line[0].isdigit():
            return self.read_nested_window_content(int(line[0]))
        elif line.startswith('V'):
            return self.handle_v_syntax(line[1:].strip())
        else:
            return self.read_file_content(line)

    def handle_v_syntax(self, json_path):
        json_data = load_json_file(config.SELECTIONS_JSON_PATH)
        if isinstance(json_data, str):
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
        if 1 <= window_number <= len(self.editors):
            editor = self.editors[window_number - 1]
            return "\n".join(self.process_line(line.strip()) for line in editor.toPlainText().splitlines())
        return ""

    def read_file_content(self, file_path):
        full_path = os.path.join(self.project_directory, file_path)
        content = read_file_content(full_path)
        if content is not None:
            return f"Content of {os.path.basename(full_path)}:\n{content}\n"
        else:
            return file_path

    def save_content(self):
        data = {
            self.project_directory: {
                f"editor{i+1}_content": editor.toPlainText()
                for i, editor in enumerate(self.editors)
            },
            "last_project_directory": self.project_directory
        }
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
                self.view.update_project_directory_label(self.project_directory)
                self.load_content()

    def close_event(self):
        self.save_content()
