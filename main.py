import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
from tkinter import ttk
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Comment, Keyword, Name, String, Error

class PythonCodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Editor")
        self.root.configure(bg="black")

        # Create text area for code input with line numbers and syntax highlighting
        self.text_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            bg="black", 
            fg="white", 
            insertbackground="white",
            font=("Courier New", 12)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.text_area.tag_configure("comment", foreground="#008B8B")
        self.text_area.tag_configure("keyword", foreground="#FFA500", font=("Courier New", 12, "bold"))
        self.text_area.tag_configure("name", foreground="#FFFFFF")
        self.text_area.tag_configure("string", foreground="#90EE90")
        self.text_area.tag_configure("error", foreground="#FF0000")

        self.update_syntax_highlighting()

        # Create frame for toolbar
        self.toolbar_frame = tk.Frame(self.root, bg="black")
        self.toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        # Add buttons to the toolbar
        self.new_button = tk.Button(self.toolbar_frame, text="New", command=self.new_file, bg="black", fg="white")
        self.new_button.pack(side=tk.LEFT, padx=5)

        self.open_button = tk.Button(self.toolbar_frame, text="Open", command=self.open_file, bg="black", fg="white")
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.toolbar_frame, text="Save", command=self.save_file, bg="black", fg="white")
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.save_as_button = tk.Button(self.toolbar_frame, text="Save As", command=self.save_file_as, bg="black", fg="white")
        self.save_as_button.pack(side=tk.LEFT, padx=5)

        self.run_button = tk.Button(self.toolbar_frame, text="Run", command=self.run_code, bg="black", fg="white")
        self.run_button.pack(side=tk.LEFT, padx=5)  # Placing the button on the left side
        
        # Add button for package installation
        self.install_package_button = tk.Button(self.toolbar_frame, text="Install Package", command=self.install_package, bg="black", fg="white")
        self.install_package_button.pack(side=tk.LEFT, padx=5)

        # Create output area for displaying results
        self.output_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5, bg="black", fg="white")
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Initialize current file path
        self.current_file = None

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.output_area.delete(1.0, tk.END)
        self.current_file = None

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                self.current_file = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.current_file = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def run_code(self):
        try:
            # Extract Python code from the text area
            python_code = self.text_area.get(1.0, tk.END)

            # Create a temporary Python file
            with open("temp.py", "w") as temp_file:
                temp_file.write(python_code)

            # Run the Python file
            run_result = subprocess.run(["python", "temp.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Display output in the output area
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, run_result.stdout)
            if run_result.stderr:
                self.output_area.insert(tk.END, "\nError:\n" + run_result.stderr)

            messagebox.showinfo("Info", "Python code executed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run code: {e}")
        finally:
            # Remove the temporary Python file
            if os.path.exists("temp.py"):
                os.remove("temp.py")

    def update_syntax_highlighting(self):
        code = self.text_area.get(1.0, tk.END)
        self.text_area.mark_set("range_start", 1.0)
        data = [(token, value) for token, value in PythonLexer().get_tokens(code)]
        for token, value in data:
            token_name = self.map_token_to_tag(token)
            self.text_area.mark_set("range_end", "range_start + %dc" % len(value))
            self.text_area.tag_add(token_name, "range_start", "range_end")
            if token == Comment:
                self.text_area.tag_add(token_name, "range_start", "range_end")
            self.text_area.mark_set("range_start", "range_end")

    def map_token_to_tag(self, token):
        if token in Comment: return "comment"
        elif token in Keyword: return "keyword"
        elif token in Name: return "name"
        elif token in String: return "string"
        else: return "error"

    def install_package(self):
        package_name = tk.simpledialog.askstring("Package Name", "Enter package name:")
        if package_name:
            try:
                result = subprocess.run(["pip", "install", package_name], capture_output=True, text=True)
                if result.returncode == 0:
                    self.output_area.config(state=tk.NORMAL)
                    self.output_area.insert(tk.END, f"Successfully installed {package_name}.\n")
                else:
                    self.output_area.config(state=tk.NORMAL)
                    self.output_area.insert(tk.END, f"Failed to install {package_name}. Error: {result.stderr}\n")
            except Exception as e:
                self.output_area.config(state=tk.NORMAL)
                self.output_area.insert(tk.END, f"Failed to install {package_name}. Error: {str(e)}\n")
            finally:
                self.output_area.config(state=tk.DISABLED)
            
# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    editor = PythonCodeEditor(root)
    root.mainloop()
