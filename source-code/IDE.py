import tkinter as tk
from tkinter import scrolledtext, filedialog, PhotoImage
import os
import threading
import re

color = {
    'output': '#00FF00',
    'input': '#00FF00',
    'set': '#00BFFF',
    'int': '#00BFFF',
    'str': '#00BFFF',
    'bool': '#00BFFF',
    'list': '#00BFFF',
    r'\n': '#8A2BE2',
    '\s': '#8A2BE2',
    '\|/': '#8A2BE2',
    '==': '#FFFF00',
    '>>': '#FFFF00',
    '<<': '#FFFF00',
    'update': '#00FF00',
    'delete': '#00FF00',
    'if': '#00FF00',
    '<-#->': '#808080',
    '=>': '#FFFF00',
    '>=': '#FFFF00',
    'block': '#00FF00',
    'run-block': '#00BFFF',
    'import': '#FF0000',
    'import_var': '#FF0000',
    'import_block': '#FF0000',
    'from': '#FF0000',
    'mods': '#FF00FF',
    'init': '#FF00FF',
    '[{': '#FF00FF',
    '}]': '#FF00FF',
}

class DarkIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Dark IDE")
        icon = PhotoImage(file='image_png.png')
        self.root.iconphoto(True, icon)
        self.root.configure(bg='#2E2E2E')
        self.current_file = None

        self.current_version = 'dark.exe'

        button_frame = tk.Frame(root, bg='#2E2E2E')
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        open_button = tk.Button(
            button_frame,
            text="Открыть",
            command=self.open_file,
            font=("Consolas", 12),
            bg='#3E3E3E',
            fg='white'
        )
        open_button.pack(side=tk.LEFT, padx=5)

        save_button = tk.Button(
            button_frame,
            text="Сохранить",
            command=self.save_file,
            font=("Consolas", 12),
            bg='#3E3E3E',
            fg='white'
        )
        save_button.pack(side=tk.LEFT, padx=5)

        version_button = tk.Button(
            button_frame,
            text="Весрия",
            command=self.version_select,
            font=("Consolas", 12),
            bg='#3E3E3E',
            fg='white'
        )
        version_button.pack(side=tk.LEFT, padx=5)

        run_button = tk.Button(
            button_frame,
            text="Запустить",
            command=self.run_code,
            font=("Consolas", 12),
            bg='#3E3E3E',
            fg='white'
        )
        run_button.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(root, bg='#2E2E2E')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.line_numbers_frame = tk.Frame(self.canvas, bg='#1E1E1E')
        self.line_numbers_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.line_numbers = tk.Text(
            self.line_numbers_frame,
            width=4,
            bg='#1E1E1E',
            fg='white',
            font=("Consolas", 12),
            padx=5,
            pady=5,
            wrap=tk.NONE,
            state='disabled'
        )
        self.line_numbers.pack(fill=tk.Y, expand=True)

        self.text_area = scrolledtext.ScrolledText(
            self.canvas,
            wrap=tk.NONE,
            font=("Consolas", 12),
            bg='#1E1E1E',
            fg='white',
            insertbackground='white'
        )
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<KeyRelease>", self.on_text_change)
        self.text_area.bind("<Configure>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self.on_mouse_wheel)

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", tk.END)

        line_count = self.text_area.index('end-1c').split('.')[0]
        for i in range(1, int(line_count) + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        self.line_numbers.config(state='disabled')

    def on_text_change(self, event=None):
        self.highlight_words()
        self.update_line_numbers()

    def on_mouse_wheel(self, event):
        self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".dark",
            filetypes=[("Dark Language Files", "*.dark"), ("All Files", "*.*")]
        )

        if file_path:
            self.current_file = file_path

            self.text_area.delete("1.0", tk.END)

            with open(file_path, 'r', encoding='utf8') as file:
                self.text_area.insert(tk.END, file.read())

            self.highlight_words()
            self.update_line_numbers()

    def version_select(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл версии",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )

        if file_path:
            self.current_version = os.path.basename(file_path)

    def save_file(self):
        if self.current_file is None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".dark",
                filetypes=[("Dark Language Files", "*.dark"), ("All Files", "*.*")]
            )
        else:
            file_path = self.current_file

        if file_path:
            with open(file_path, 'w', encoding='utf8') as file:
                file.write(self.text_area.get("1.0", tk.END))

            self.current_file = file_path

    def run_code(self):
        if self.current_file is None:
            self.save_file()

        if self.current_file is None:
            return

        threading.Thread(target=self.run_in_terminal, args=(self.current_file,)).start()

    def run_in_terminal(self, file_path):
        os.system(f"{self.current_version} {file_path}")
        # os.system(f"python {self.current_version} {file_path}")

    def highlight_words(self, event=None):
        self.text_area.tag_remove("highlight", "1.0", tk.END)

        text = self.text_area.get("1.0", tk.END)

        words = re.findall(r'\S+', text)

        for word in words:
            if word in color:
                start_index = self.text_area.search(word, "1.0", tk.END)
                while start_index:
                    end_index = f"{start_index}+{len(word)}c"
                    tag_name = f"tag_{word}"
                    if tag_name not in self.text_area.tag_names():
                        self.text_area.tag_configure(tag_name, foreground=color[word])
                    self.text_area.tag_add(tag_name, start_index, end_index)
                    start_index = self.text_area.search(word, end_index, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    ide = DarkIDE(root)
    root.mainloop()
