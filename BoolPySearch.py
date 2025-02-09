
# © 2025 Muhammad Ahmad Sultan - BoolPySearch. All Rights Reserved

import os     # For file handling
import re     # For regular expressions
from collections import defaultdict     # For creating an inverted index
import tkinter as tk      # For GUI
from tkinter import ttk, filedialog, messagebox    # For UI elements
from tkinter import scrolledtext                   # For scrollable text box

# --- Boolean Search Functions ---
# --- Core Search Engine Components ---

# Common English stopwords to be filtered out during text processing
stopwords = set(["a", "an", "the", "is", "in", "of", "for", "and", "to", "on", "by", "that", "it", "from", "this", "with", "as", "at", "are", "was", "were", "has", "have", "had", "be", "been", "but", "or", "not", "which", "will", "through"])

def preprocess(text):
    """
    Tokenizes and preprocesses text by converting to lowercase and removing stopwords.
    Args:
        text (str): Raw input text
    Returns:
        list: List of processed tokens excluding stopwords
    """
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [token for token in tokens if token not in stopwords]

def load_documents_from_folder(folder_path):
    """
    Loads all .txt files from the specified folder into a dictionary.
    Args:
        folder_path (str): Path to folder containing text documents
    Returns:
        dict: Dictionary mapping filenames to document contents
    """
    documents = {}
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file: 
                    documents[filename] = file.read()
    except Exception as e:
        messagebox.showerror("Error", f"Error reading documents: {e}")
        return {}
    return documents

def create_inverted_index(documents):
    """
    Creates an inverted index mapping terms to the documents containing them.
    Args:
        documents (dict): Dictionary of document contents
    Returns:
        defaultdict: Inverted index mapping terms to sets of document IDs
    """
    inverted_index = defaultdict(set)
    for doc_id, text in documents.items():
        tokens = preprocess(text)
        for token in tokens:
            inverted_index[token].add(doc_id)
    return inverted_index

def boolean_and_search(query, inverted_index):
    query_terms = preprocess(query)
    if not query_terms:
        return set()
    result = inverted_index[query_terms[0]]
    for term in query_terms[1:]:
        result = result.intersection(inverted_index[term])
    return result

def boolean_or_search(query, inverted_index):
    query_terms = preprocess(query)
    if not query_terms:
        return set()
    result = set()
    for term in query_terms:
        result = result.union(inverted_index[term])
    return result

def boolean_not_search(query, inverted_index, all_docs):
    query_terms = preprocess(query)
    if not query_terms:
        return set()
    result = all_docs.copy()
    for term in query_terms:
        result = result.difference(inverted_index[term])
    return result

# --- GUI Class ---
class BoolPySearch:
    def __init__(self, root):
        self.root = root
        self.root.title("BoolPySearch v1.0.0")
        self.root.geometry("870x755")  
        
        self.center_window()
        

        # Theme colors
        self.bg_color = "#191A19"
        self.fg_color = "#D8E9A8"
        self.button_bg = "#1E5128"
        self.button_fg = "#D8E9A8"
        self.accent_color = "#4E9F3D"
        self.font_size = 12  
        self.entry_font_size = 14 

        # Apply theme
        self.root.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.style.theme_use('clam')  

        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Arial", self.font_size))
        self.style.configure("TButton", background=self.button_bg, foreground=self.button_fg, borderwidth=2, highlightthickness=0, font=("Arial", self.font_size), relief="groove", padding=6)
        self.style.map("TButton", background=[("active", self.accent_color)])
        self.style.configure("TEntry", fieldbackground=self.bg_color, foreground=self.fg_color, borderwidth=0, highlightthickness=0, font=("Arial", self.entry_font_size))
        self.style.configure("TCombobox", fieldbackground="#1E5128", background="#4E9F3D", foreground="#D8E9A8", font=("Arial", 14))
        self.style.configure("Vertical.TScrollbar", background=self.bg_color, borderwidth=0, highlightthickness=0)
        self.style.map("TCombobox", fieldbackground=[("readonly", "#1E5128")])
        self.style.configure("Clear.TButton", background="#B82132", foreground=self.button_fg, font=("Arial", self.font_size), relief="groove", padding=6)
        self.style.map("Clear.TButton", background=[("active", "#CC2B52")])  
        self.style.configure("Exit.TButton", background="#B82132", foreground="#D8E9A8", font=("Arial", self.font_size), relief="groove", padding=6)
        self.style.map("Exit.TButton", background=[("active", "#CC2B52")])  

        # Data
        self.documents = {}
        self.inverted_index = {}
        self.folder_path = ""

        # --- GUI Elements ---
        # Title Label
        title_label = ttk.Label(root, text="BoolPySearch", font=("Arial", 21))
        title_label.pack(pady=12)

        # Version Label
        version_label = ttk.Label(root, text="Version: BoolPySearch v1.0.0", font=("Arial", 11))
        version_label.pack()

        # Developer Label
        developer_label = ttk.Label(root, text="Developed by Muhammad Ahmad Sultan", font=("Arial", 11))
        developer_label.pack()

        # Load Documents Button
        self.load_button = ttk.Button(root, text="Load Documents 📁", command=self.load_documents, style="TButton")
        self.load_button.pack(pady=8)

        # Documents Loaded Label
        self.doc_count_label = ttk.Label(root, text="Total Documents Loaded: 0")
        self.doc_count_label.pack()

        # Inverted Index Display
        self.index_label = ttk.Label(root, text="Inverted Index:")
        self.index_label.pack(pady=5)
        self.index_text = scrolledtext.ScrolledText(root, width=80, height=10, bg=self.bg_color, fg=self.fg_color, font=("Arial", self.font_size))
        self.index_text.pack(pady=7)
        self.index_text.config(state=tk.DISABLED)  # Make read-only

        # Search Frame
        self.style.configure("Search.TFrame", background="#ffeeb4")
        search_frame = ttk.Frame(root, padding=12, style="Search.TFrame")
        search_frame.pack()

        # Search Type (Combobox)
        self.search_type_label = ttk.Label(search_frame, text="Search Type:")
        self.search_type_label.grid(row=0, column=0, padx=5, ipady=2.5)

        self.search_type = ttk.Combobox(
            search_frame, 
            values=["AND", "OR", "NOT"], 
            state="readonly", 
            width=6,  
            font=("Arial", 14)  
        )
        self.search_type.grid(row=0, column=1, padx=5, ipady=2.5)  
        self.search_type.set("AND")
        self.search_type.bind("<<ComboboxSelected>>", self.update_combobox_style)

        # Query Entry
        self.query_label = ttk.Label(search_frame, text="Enter Query:")
        self.query_label.grid(row=0, column=2, padx=5, ipady=2.5)
        
        # Query Entry (Increased height & font size)
        self.query_entry = ttk.Entry(search_frame, width=24, font=("Arial", 13))  # Increased font size
        self.query_entry.grid(row=0, column=3, padx=5, ipady=2.5)  # Increased height using ipady

        # Search Button
        self.search_button = ttk.Button(search_frame, text="Search 🔍", command=self.perform_search, style="TButton")
        self.search_button.grid(row=0, column=4, padx=5)

        # Clear Button
        self.clear_button = ttk.Button(search_frame, text="Reset ♻️", command=self.clear_all, style="Clear.TButton")
        self.clear_button.grid(row=0, column=5, padx=5)

        # Search Results
        self.results_label = ttk.Label(root, text="Search Results:", font=("Arial", 13))
        self.results_label.pack(pady=5)
        self.results_text = scrolledtext.ScrolledText(root, width=80, height=10, bg=self.bg_color, fg=self.fg_color, font=("Arial", self.font_size))
        self.results_text.pack(pady=7)
        self.results_text.config(state=tk.DISABLED)

        # Exit Button
        self.exit_button = ttk.Button(root, text="Exit ❌", command=self.exit_application, style="Exit.TButton")
        self.exit_button.pack(pady=8)

        self.update_combobox_style() # Initial styling

    # --- GUI Actions ---
    def load_documents(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.documents = load_documents_from_folder(self.folder_path)
            if self.documents:
                self.inverted_index = create_inverted_index(self.documents)
                self.doc_count_label.config(text=f"Total Documents Loaded: {len(self.documents)}")
                self.display_inverted_index()
                messagebox.showinfo("Success", "Documents loaded successfully!")
            else:
                messagebox.showinfo("Info", "No documents found in the selected folder.")

    def display_inverted_index(self):
        self.index_text.config(state=tk.NORMAL)  # Enable editing
        self.index_text.delete("1.0", tk.END)  # Clear existing text
        for term, doc_ids in self.inverted_index.items():
            self.index_text.insert(tk.END, f"{term}: {doc_ids}\n")
        self.index_text.config(state=tk.DISABLED)  # Disable editing

    def perform_search(self):
        query = self.query_entry.get()
        search_type = self.search_type.get()
        all_docs = set(self.documents.keys())

        if not self.inverted_index:
            messagebox.showinfo("Info", "Please load documents first.")
            return

        if not query:
            messagebox.showinfo("Info", "Please enter a query.")
            return

        if search_type == "AND":
            result = boolean_and_search(query, self.inverted_index)
        elif search_type == "OR":
            result = boolean_or_search(query, self.inverted_index)
        elif search_type == "NOT":
            result = boolean_not_search(query, self.inverted_index, all_docs)
        else:
            messagebox.showerror("Error", "Invalid search type.")
            return

        self.display_search_results(result)

    def display_search_results(self, result):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)

        if not result:
            self.results_text.insert(tk.END, "No documents found matching the query.")
        else:
            for doc_id in result:
                self.results_text.insert(tk.END, f"Document: {doc_id}\n")
                self.results_text.insert(tk.END, self.documents[doc_id] + "\n\n")  # Display document content
        self.results_text.config(state=tk.DISABLED)

    def clear_all(self):
        # Clear search results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)

        # Clear inverted index display
        self.index_text.config(state=tk.NORMAL)
        self.index_text.delete("1.0", tk.END)
        self.index_text.config(state=tk.DISABLED)

        # Clear query entry
        self.query_entry.delete(0, tk.END)

        # Reset document count
        self.doc_count_label.config(text="Total Documents Loaded: 0")

        # Reset data
        self.documents = {}
        self.inverted_index = {}
        self.folder_path = ""

    def exit_application(self):
        self.root.destroy()

    def update_combobox_style(self, event=None):
        selected_value = self.search_type.get()
        if selected_value == "AND":
            self.style.configure("TCombobox", fieldbackground="#1E5128", foreground="#D8E9A8")
        elif selected_value == "OR":
            self.style.configure("TCombobox", fieldbackground="#4E9F3D", foreground="#191A19")
        elif selected_value == "NOT":
            self.style.configure("TCombobox", fieldbackground="#D8E9A8", foreground="#191A19")
        else:
            self.style.configure("TCombobox", fieldbackground=self.bg_color, foreground=self.fg_color)
            
    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 870
        window_height = 755

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")        


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BoolPySearch(root)

    root.mainloop()
    
    