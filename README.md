# File Content Reader Application

This is a simple Python application that uses `Tkinter` to create a GUI for reading and displaying file content based on Git changes. The program allows users to fetch the list of modified files from a Git repository, read the content of these files, and copy the content to the clipboard. It also provides functionality to save and load the contents of two textboxes for persistence between application runs.

![image](https://github.com/user-attachments/assets/f6e74f7b-7dd2-4090-b545-966b40b13b06)


## Features

- Fetches the list of changed files in a Git repository using `git status`.
- Displays file paths of modified files in a text box.
- Reads and copies the content of files listed in the text box.
- Saves the content of the text boxes to a JSON file upon closing the application and loads it upon reopening.
- Supports listing files inside directories and reading their content.
- Auto-updates line numbers for better readability.

## Requirements

To run this program, the following Python packages are required:

- `tkinter` (part of the standard library)
- `pyperclip` for copying file content to the clipboard
- `git` command-line tool should be available and properly configured

### Installation

1. Clone or download this repository to your local machine.
2. Install the required dependencies by running:

```bash
pip install pyperclip
```

3. Make sure that `git` is installed and added to your system's PATH.

### How to Use

1. Adjust the `project_directory` variable to point to your Git project directory.
2. Run the Python program using the command:

```bash
python file_content_reader.py
```

3. The following features are available:
   - **Get Git Changes**: Fetches the modified files in the Git repository and displays them in the first text box.
   - **Read Content 1**: Reads the content of the files listed in the first text box and copies it to the clipboard.
   - **Read Content 2**: Reads the content of the files listed in the second text box and copies it to the clipboard.

### File Saving and Loading

- The application automatically saves the content of both text boxes to a file named `textboxes_content.json` located in the `save_data` folder.
- Upon restarting the application, it will load the previously saved content, allowing you to resume where you left off.

### Project Structure

```
/file_content_reader
│
├── file_content_reader.py  # Main program
├── save_data               # Directory for saving textbox content
│   └── textboxes_content.json
└── README.md               # This file
```

### Customization

You can modify the following parameters to customize the program for your needs:

- **project_directory**: Adjust this to point to your specific project folder.
- **save_folder and save_file**: Modify these variables if you'd like to save the content to a different location or file.

### License

This project is open-source and licensed under the MIT License.

Enjoy using the File Content Reader!
