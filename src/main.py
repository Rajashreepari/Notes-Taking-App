import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class Note:
    def __init__(self, title, content, tags=None, timestamp=None):
        self.title = title
        self.content = content
        self.tags = tags or []
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'timestamp': self.timestamp
        }

    def from_dict(data):
        return Note(
            title=data['title'],
            content=data['content'],
            tags=data.get('tags', []),
            timestamp=data.get('timestamp')
        )


class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note-Taking App")
        self.root.geometry("900x600")
        self.root.configure(bg="#F5F5F5")  # Light Gray Background

        self.notes = []
        self.load_notes()

        self.setup_styles()

        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')

        style.configure('TFrame', background='#F5F5F5')
        style.configure('TLabel', background='#F5F5F5', foreground='#333333', font=('Arial', 12))
        style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'))
        style.map('TButton',
                  background=[('active', '#66BB6A')])

        style.configure('Search.TEntry', foreground='#333333', font=('Arial', 10))
        style.configure('Title.TEntry', foreground='#333333', font=('Arial', 12, 'bold'))
        style.configure('Tags.TEntry', foreground='#333333', font=('Arial', 10))

        style.configure("Custom.TListbox", background='white', foreground='#333333', font=('Arial', 10))

    def create_widgets(self):
        self.root.columnconfigure(0, weight=1, uniform="group1")
        self.root.columnconfigure(1, weight=3, uniform="group1")
        self.root.rowconfigure(0, weight=1)

        self.left_frame = ttk.Frame(self.root, padding=(20, 20))
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        header_label = ttk.Label(self.left_frame, text="📒 Your Notes", font=('Arial', 16, 'bold'))
        header_label.pack(anchor='w', pady=(0, 10))

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.left_frame, textvariable=self.search_var, style='Search.TEntry')
        self.search_entry.pack(fill='x', pady=(0, 10), ipady=5)
        self.search_entry.insert(0, "🔍 Search...")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_search_placeholder)
        self.search_entry.bind("<KeyRelease>", self.search_notes)

        self.listbox_frame = ttk.Frame(self.left_frame)
        self.listbox_frame.pack(fill='both', expand=True)

        self.notes_listbox = tk.Listbox(self.listbox_frame, selectbackground='#4CAF50', selectforeground='white',
                                       font=('Arial', 10), bd=0, highlightthickness=0, activestyle='none')
        self.notes_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(self.listbox_frame, orient='vertical', command=self.notes_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.notes_listbox.config(yscrollcommand=scrollbar.set)

        self.notes_listbox.bind('<<ListboxSelect>>', self.display_note)

        self.right_frame = ttk.Frame(self.root, padding=(20, 20), style='TFrame')
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(self.right_frame, text="✏️ Title:", style='TLabel').pack(anchor='w')
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(self.right_frame, textvariable=self.title_var, style='Title.TEntry', font=('Arial', 12))
        self.title_entry.pack(fill='x', pady=(0, 10), ipady=5)

        ttk.Label(self.right_frame, text="📝 Content:", style='TLabel').pack(anchor='w')
        self.content_text = tk.Text(self.right_frame, height=15, font=('Arial', 11), bg='white', fg='#333333',
                                    bd=1, relief='solid', wrap='word')
        self.content_text.pack(fill='both', expand=True, pady=(0, 10))

        ttk.Label(self.right_frame, text="🏷️ Tags (comma separated):", style='TLabel').pack(anchor='w')
        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(self.right_frame, textvariable=self.tags_var, style='Tags.TEntry', font=('Arial', 10))
        self.tags_entry.pack(fill='x', pady=(0, 10), ipady=5)

        self.button_frame = ttk.Frame(self.right_frame)
        self.button_frame.pack(fill='x', pady=(10, 0))

        self.add_button = ttk.Button(self.button_frame, text="➕ Add Note", command=self.add_note)
        self.add_button.pack(side='left', expand=True, fill='x')

        self.update_button = ttk.Button(self.button_frame, text="✏️ Update Note", command=self.update_note)
        self.update_button.pack(side='left', expand=True, fill='x', padx=(10, 10))

        self.delete_button = ttk.Button(self.button_frame, text="🗑️ Delete Note", command=self.delete_note)
        self.delete_button.pack(side='left', expand=True, fill='x')

        self.populate_notes()

    def clear_search_placeholder(self, event):
        if self.search_entry.get() == "🔍 Search...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground='#333333')

    def add_search_placeholder(self, event):
        if not self.search_var.get():
            self.search_entry.insert(0, "🔍 Search...")
            self.search_entry.config(foreground='#888888')

    def populate_notes(self):
        self.notes_listbox.delete(0, tk.END)
        for note in self.notes:
            self.notes_listbox.insert(tk.END, note.title)

    def add_note(self):
        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]

        if not title:
            messagebox.showwarning("Input Error", "✋ Title cannot be empty.")
            return

        new_note = Note(title, content, tags)
        self.notes.append(new_note)
        self.populate_notes()
        self.save_notes()
        self.clear_fields()

    def display_note(self, event):
        selection = self.notes_listbox.curselection()
        if selection:
            index = selection[0]
            selected_note = self.notes[index]
            self.title_var.set(selected_note.title)
            self.content_text.delete("1.0", tk.END)
            self.content_text.insert(tk.END, selected_note.content)
            self.tags_var.set(", ".join(selected_note.tags))

    def update_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "⚠️ No note selected to update.")
            return

        index = selection[0]
        note = self.notes[index]

        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]

        if not title:
            messagebox.showwarning("Input Error", "✋ Title cannot be empty.")
            return

        note.title = title
        note.content = content
        note.tags = tags
        note.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.populate_notes()
        self.save_notes()
        self.clear_fields()

    def delete_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "⚠️ No note selected to delete.")
            return

        index = selection[0]
        note = self.notes.pop(index)
        self.populate_notes()
        self.save_notes()
        self.clear_fields()

    def search_notes(self, event):
        keyword = self.search_var.get().lower()
        self.notes_listbox.delete(0, tk.END)
        for note in self.notes:
            if (keyword in note.title.lower()) or any(keyword in tag.lower() for tag in note.tags):
                self.notes_listbox.insert(tk.END, note.title)

    def clear_fields(self):
        self.title_var.set("")
        self.content_text.delete("1.0", tk.END)
        self.tags_var.set("")

    def save_notes(self, filename='notes.json'):
        with open(filename, 'w') as f:
            json.dump([note.to_dict() for note in self.notes], f, indent=4)
        print("💾 Notes saved to file.")

    def load_notes(self, filename='notes.json'):
        try:
            with open(filename, 'r') as f:
                notes_data = json.load(f)
                self.notes = [Note.from_dict(note) for note in notes_data]
            print("📂 Notes loaded from file.")
        except FileNotFoundError:
            print("📄 No existing notes found. Starting fresh.")
            self.notes = []
        except json.JSONDecodeError:
            print("❌ Error decoding notes file. Starting fresh.")
            self.notes = []

def main():
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
