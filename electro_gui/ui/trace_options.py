# ui/trace_options.py
import tkinter as tk
from tkinter import ttk

def apply_trace_style_from_panel(panel, trace_label, traces, dataframes, ax):
    style = panel.get_trace_style()
    df = dataframes[trace_label]

    # Apply cycle filtering
    if style['cycle'] > 0 and 'cycle' in df.columns:
        df = df[df['cycle'] == style['cycle']]

    line = traces[trace_label]
    line.set_data(df['Ewe'], df['I'])
    line.set_color(style['color'])
    line.set_linestyle(style['linestyle'])
    line.set_linewidth(style['linewidth'])

    ax.relim()
    ax.autoscale_view()
    ax.legend()

class TraceOptionsPanel(tk.Frame):
    def __init__(self, parent, apply_callback):
        super().__init__(parent)
        self.apply_callback = apply_callback

        tk.Label(self, text="Trace Appearance").pack(anchor=tk.W, pady=(5, 2))

        self.color_var = tk.StringVar(value="blue")
        tk.Label(self, text="Color:").pack(anchor=tk.W)
        self.color_box = ttk.Combobox(self, textvariable=self.color_var,
                                      values=["blue", "red", "green", "black", "orange"],
                                      state="readonly")
        self.color_box.pack(fill=tk.X)

        self.line_style_var = tk.StringVar(value="-")
        tk.Label(self, text="Line Style:").pack(anchor=tk.W)
        self.line_style_box = ttk.Combobox(self, textvariable=self.line_style_var,
                                           values=["-", "--", "-.", ":"],
                                           state="readonly")
        self.line_style_box.pack(fill=tk.X)

        self.line_width_var = tk.DoubleVar(value=1.5)
        tk.Label(self, text="Line Width:").pack(anchor=tk.W)
        tk.Spinbox(self, from_=0.5, to=5.0, increment=0.1,
                   textvariable=self.line_width_var, width=5).pack(fill=tk.X)

        self.cycle_var = tk.IntVar(value=0)
        tk.Label(self, text="Cycle Number (0 = all):").pack(anchor=tk.W)
        tk.Spinbox(self, from_=0, to=100, textvariable=self.cycle_var, width=5).pack(fill=tk.X)

        # Dynamic update on change
        self._register_traces()

    def _update(self, *args):
        if self.apply_callback:
            self.apply_callback()

    def get_trace_style(self):
        return {
            'color': self.color_var.get(),
            'linestyle': self.line_style_var.get(),
            'linewidth': self.line_width_var.get(),
            'cycle': self.cycle_var.get()
        }

    def set_trace_style_from_line(self, line):
        # Temporarily disable update callback
        self.color_var.trace_remove("write", self._color_trace)
        self.line_style_var.trace_remove("write", self._style_trace)
        self.line_width_var.trace_remove("write", self._width_trace)
        self.cycle_var.trace_remove("write", self._cycle_trace)

        self.color_var.set(line.get_color())
        self.line_style_var.set(line.get_linestyle())
        self.line_width_var.set(line.get_linewidth())
        self.cycle_var.set(0)

        # Re-enable update callback
        self._register_traces()

    def _register_traces(self):
        self._color_trace = self.color_var.trace_add("write", self._update)
        self._style_trace = self.line_style_var.trace_add("write", self._update)
        self._width_trace = self.line_width_var.trace_add("write", self._update)
        self._cycle_trace = self.cycle_var.trace_add("write", self._update)
