# ui/graph_options.py
import tkinter as tk
from tkinter import ttk

def apply_graph_settings_from_panel(panel, ax):
    (xmin, xmax), (ymin, ymax) = panel.get_axis_limits()
    xlabel, ylabel = panel.get_axis_labels()

    if xmin != xmax:
        ax.set_xlim(xmin, xmax)
    if ymin != ymax:
        ax.set_ylim(ymin, ymax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

class GraphOptionsPanel(tk.Frame):
    def __init__(self, parent, apply_callback):
        super().__init__(parent)
        self.apply_callback = apply_callback

        tk.Label(self, text="Graph Options").pack(anchor=tk.W, pady=(5, 2))

        self.xmin = tk.DoubleVar()
        self.xmax = tk.DoubleVar()
        self.ymin = tk.DoubleVar()
        self.ymax = tk.DoubleVar()

        self.xlabel = tk.StringVar(value="Potential")
        self.ylabel = tk.StringVar(value="Current")

        tk.Label(self, text="X Range (min/max):").pack(anchor=tk.W)
        x_range = tk.Frame(self)
        tk.Entry(x_range, textvariable=self.xmin, width=8).pack(side=tk.LEFT)
        tk.Entry(x_range, textvariable=self.xmax, width=8).pack(side=tk.LEFT)
        x_range.pack()

        tk.Label(self, text="Y Range (min/max):").pack(anchor=tk.W)
        y_range = tk.Frame(self)
        tk.Entry(y_range, textvariable=self.ymin, width=8).pack(side=tk.LEFT)
        tk.Entry(y_range, textvariable=self.ymax, width=8).pack(side=tk.LEFT)
        y_range.pack()

        tk.Label(self, text="X Axis Label:").pack(anchor=tk.W)
        tk.Entry(self, textvariable=self.xlabel).pack(fill=tk.X)

        tk.Label(self, text="Y Axis Label:").pack(anchor=tk.W)
        tk.Entry(self, textvariable=self.ylabel).pack(fill=tk.X)

        # Dynamic update on change
        self.xmin.trace_add("write", self._update)
        self.xmax.trace_add("write", self._update)
        self.ymin.trace_add("write", self._update)
        self.ymax.trace_add("write", self._update)
        self.xlabel.trace_add("write", self._update)
        self.ylabel.trace_add("write", self._update)

    def _update(self, *args):
        if self.apply_callback:
            self.apply_callback()

    def get_axis_limits(self):
        return (self.xmin.get(), self.xmax.get()), (self.ymin.get(), self.ymax.get())

    def get_axis_labels(self):
        return self.xlabel.get(), self.ylabel.get()


