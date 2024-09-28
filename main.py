import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import pyperclip
import json

# Set the project directory (adjust as needed)
project_directory = r"C:\Users\morge\Desktop\Work\RSM2"

# Define the save folder and file path within the Python project directory
save_folder = os.path.join(os.path.dirname(__file__), "save_data")
os.makedirs(save_folder, exist_ok=True)
save_file = os.path.join(save_folder, "textboxes_content.json")

# Function to get changed files from Git and populate textbox1
def getGitChanges():
    os.chdir(project_directory)
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        changed_files = result.stdout.splitlines()
        file_paths = [file[3:] for file in changed_files if len(file) > 3]

        # Clear textbox1 and insert paths
        textbox1.delete("1.0", tk.END)
        for path in file_paths:
            absolute_path = os.path.join(project_directory, path.strip())
            # Check if it's a file; if it's a directory, list files inside
            if os.path.isfile(absolute_path):
                textbox1.insert(tk.END, path + "\n")
            elif os.path.isdir(absolute_path):
                for root, _, files in os.walk(absolute_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, project_directory)
                        textbox1.insert(tk.END, relative_path + "\n")
        update_line_numbers(textbox1, line_numbers1)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get Git changes: {e}")

# Function to read file content from textbox1
def read_content1():
    file_paths = textbox1.get("1.0", tk.END).strip().split("\n")
    content = ""
    copied_files_count = 0
    for file_path in file_paths:
        if file_path:
            full_path = os.path.join(project_directory, file_path.strip())
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content += f"Content of {file_path}:\n{f.read()}\n{'-' * 80}\n"
                        copied_files_count += 1
                except Exception as e:
                    content += f"Failed to read {file_path}: {e}\n"
            else:
                content += f"Skipped: {file_path} (not a file or deleted).\n"
    pyperclip.copy(content)
    messagebox.showinfo("Info", f"Content copied to clipboard. Total files copied: {copied_files_count}")

# Function to read file content from textbox2
def read_content2():
    file_paths = textbox2.get("1.0", tk.END).strip().split("\n")
    content = ""
    copied_files_count = 0
    for file_path in file_paths:
        if file_path:
            full_path = os.path.join(project_directory, file_path.strip())
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content += f"Content of {file_path}:\n{f.read()}\n{'-' * 80}\n"
                        copied_files_count += 1
                except Exception as e:
                    content += f"Failed to read {file_path}: {e}\n"
            else:
                content += f"Skipped: {file_path} (not a file or deleted).\n"
    pyperclip.copy(content)
    messagebox.showinfo("Info", f"Content copied to clipboard. Total files copied: {copied_files_count}")

# Function to save the content of textboxes to a file
def save_content():
    data = {
        "textbox1": textbox1.get("1.0", tk.END).strip(),
        "textbox2": textbox2.get("1.0", tk.END).strip(),
    }
    with open(save_file, "w") as f:
        json.dump(data, f)

# Function to load the content of textboxes from a file
def load_content():
    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            data = json.load(f)
            textbox1.insert(tk.END, data.get("textbox1", "").strip())
            textbox2.insert(tk.END, data.get("textbox2", "").strip())
            update_line_numbers(textbox1, line_numbers1)
            update_line_numbers(textbox2, line_numbers2)

# Function to update the line numbers for the textboxes
def update_line_numbers(textbox, line_numbers):
    line_count = int(textbox.index('end-1c').split('.')[0])
    line_numbers.config(state='normal')
    line_numbers.delete('1.0', tk.END)
    line_numbers.insert(tk.END, "\n".join(str(i) for i in range(1, line_count + 1)))
    line_numbers.config(state='disabled')

# Function to create a frame with a textbox and line numbers
def create_textbox_frame(parent):
    frame = tk.Frame(parent)

    # Create line numbers textbox
    line_numbers = tk.Text(frame, width=4, padx=4, takefocus=0, border=0, background='lightgrey', state='disabled')
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    # Create main textbox
    textbox = tk.Text(frame, height=20, width=80)
    textbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Bind event to update line numbers when content changes
    textbox.bind("<KeyRelease>", lambda event: update_line_numbers(textbox, line_numbers))

    return frame, textbox, line_numbers

# Create the main window
root = tk.Tk()
root.title("File Content Reader")

# Create the first textbox and button
frame1, textbox1, line_numbers1 = create_textbox_frame(root)
frame1.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

button1 = tk.Button(root, text="Get Git Changes", command=getGitChanges)
button1.pack(pady=5)

read_button1 = tk.Button(root, text="Read Content 1", command=read_content1)
read_button1.pack(pady=5)

# Create the second textbox and button
frame2, textbox2, line_numbers2 = create_textbox_frame(root)
frame2.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

read_button2 = tk.Button(root, text="Read Content 2", command=read_content2)
read_button2.pack(pady=5)

# Load content from the save file when the application starts
load_content()

# Save content to the save file when the application closes
root.protocol("WM_DELETE_WINDOW", lambda: (save_content(), root.destroy()))

# Start the main loop
root.mainloop()
