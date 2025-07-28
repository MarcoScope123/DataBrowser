# ui/app.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core import loader
from ui.trace_options import TraceOptionsPanel, apply_trace_style_from_panel
from ui.graph_options import GraphOptionsPanel, apply_graph_settings_from_panel

class DataBrowserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Electrochemical Data Browser")
        self.geometry("1280x720")

        self.folder = None
        self.traces = {}  # label -> Line2D
        self.dataframes = {}  # label -> DataFrame
        self.current_trace = None

        self._build_ui()

    def _build_ui(self):
        # Top control bar
        top = tk.Frame(self); top.pack(fill=tk.X, padx=6, pady=4)

        tk.Button(top, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT)
        self.folder_label = tk.StringVar()
        tk.Entry(top, textvariable=self.folder_label, width=40, state='readonly').pack(side=tk.LEFT, padx=5)

        tk.Label(top, text="Filetype:").pack(side=tk.LEFT, padx=5)
        self.ftype_box = ttk.Combobox(top, values=[".mpt", ".txt"], state="readonly", width=6)
        self.ftype_box.current(0)
        self.ftype_box.pack(side=tk.LEFT)

        tk.Label(top, text="Data Type:").pack(side=tk.LEFT, padx=5)
        self.dtype_box = ttk.Combobox(top, values=["cv", "eis"], state="readonly", width=6)
        self.dtype_box.current(0)
        self.dtype_box.pack(side=tk.LEFT)

        # tk.Label(top, text="Sub-Type:").pack(side=tk.LEFT, padx=5)
        # self.subtype_box = ttk.Combobox(top, values=[""], state="readonly", width=6)
        # self.subtype_box.current(0)
        # self.subtype_box.pack(side=tk.LEFT)

        tk.Button(top, text="Export Plot", command=self.export_plot).pack(side=tk.RIGHT, padx=10)

        # Main body
        body = tk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        # Left panel: file list
        left = tk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        tk.Label(left, text="Files in Folder").pack()
        self.file_listbox = tk.Listbox(left, height=20)
        self.file_listbox.pack(fill=tk.Y, expand=True)
        tk.Button(left, text="Add to Plot", command=self.add_selected_file).pack(pady=5)

        # Center: plot area
        center = tk.Frame(body, bd=2, relief=tk.SUNKEN)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=center)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Right panel: trace controls and options
        right = tk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Label(right, text="Traces").pack()
        self.trace_listbox = tk.Listbox(right, height=10)
        self.trace_listbox.pack(fill=tk.X)
        self.trace_listbox.bind("<<ListboxSelect>>", self.on_trace_select)
        tk.Button(right, text="Remove Trace", command=self.remove_selected_trace).pack(pady=5)
        tk.Button(right, text="Duplicate Trace", command=self.duplicate_trace).pack(pady=2)
        tk.Button(right, text="Rename Trace", command=self.rename_trace).pack(pady=2)

        # Trace options panel
        self.trace_options = TraceOptionsPanel(right, apply_callback=self.apply_trace_options)
        self.trace_options.pack(fill=tk.X, pady=4)

        # Graph options panel
        self.graph_options = GraphOptionsPanel(right, apply_callback=self.apply_graph_options)
        self.graph_options.pack(fill=tk.X, pady=4)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.folder = folder
        self.folder_label.set(folder)
        self._refresh_file_list()

    def _refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        import os
        for file in sorted(os.listdir(self.folder)):
            if file.endswith(".txt"):
                self.file_listbox.insert(tk.END, file)
            elif file.endswith(".mpt"):
                self.file_listbox.insert(tk.END, file)

    def add_selected_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            return
        filename = self.file_listbox.get(selected[0])
        path = f"{self.folder}/{filename}"
        ftype = self.ftype_box.get()
        dtype = self.dtype_box.get()
        #subtype = self.subtype_box.get() or None

        try:
            df = loader.load(path, ftype, dtype)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            return

        label = filename
        self.dataframes[label] = df
        #here it would be best to have a "style" function
        line, = self.ax.plot(df["Ewe"], df["I"], label=label)
        self.traces[label] = line
        self.trace_listbox.insert(tk.END, label)
        self.ax.set_xlabel("Potential")
        self.ax.set_ylabel("Current")
        self.ax.legend()
        self.canvas.draw()

    def on_trace_select(self, event):
        selection = self.trace_listbox.curselection()
        if selection:
            self.current_trace = self.trace_listbox.get(selection[0])
            line = self.traces[self.current_trace]
            self.trace_options.set_trace_style_from_line(line)

    def remove_selected_trace(self):
        if not self.current_trace:
            return
        self.traces[self.current_trace].remove()
        self.trace_listbox.delete(self.trace_listbox.get(0, tk.END).index(self.current_trace))
        del self.traces[self.current_trace]
        del self.dataframes[self.current_trace]
        self.current_trace = None
        self.ax.legend()
        self.canvas.draw()

    def export_plot(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if not path:
            return
        self.fig.savefig(path, dpi=300)
        messagebox.showinfo("Export", f"Plot saved to {path}")

    def apply_trace_options(self):
        if not self.current_trace:
            return
        apply_trace_style_from_panel(self.trace_options, self.current_trace, self.traces, self.dataframes, self.ax)
        self.canvas.draw()

    def apply_graph_options(self):
        apply_graph_settings_from_panel(self.graph_options, self.ax)
        self.canvas.draw()

    def duplicate_trace(self):
        if not self.current_trace:
            return
        base_label = self.current_trace
        new_label = f"{base_label}_copy"
        i = 1
        while new_label in self.traces:
            new_label = f"{base_label}_copy{i}"
            i += 1
        df = self.dataframes[base_label].copy()
        self.dataframes[new_label] = df
        line, = self.ax.plot(df["Ewe"], df["I"], label=new_label)
        self.traces[new_label] = line
        self.trace_listbox.insert(tk.END, new_label)
        self.ax.legend()
        self.canvas.draw()

    def rename_trace(self):
        if not self.current_trace:
            return
        new_name = tk.simpledialog.askstring("Rename Trace", "Enter new name:")
        if not new_name or new_name in self.traces:
            return
        line = self.traces.pop(self.current_trace)
        df = self.dataframes.pop(self.current_trace)

        self.traces[new_name] = line
        self.dataframes[new_name] = df
        line.set_label(new_name)

        idx = self.trace_listbox.get(0, tk.END).index(self.current_trace)
        self.trace_listbox.delete(idx)
        self.trace_listbox.insert(idx, new_name)
        self.current_trace = new_name
        self.ax.legend()
        self.canvas.draw()
