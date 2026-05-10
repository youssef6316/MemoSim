import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List
from Controller.memory_manager import MemoryManager
from Controller.models import Process, Segment

# ====== Color Palette (Dark/Amber/Charcoal) ======
COLORS = {
    "bg_dark": "#1e1e2e",
    "bg_card": "#2a2a3c",
    "bg_input": "#232334",
    "fg_main": "#cdd6f4",
    "fg_dim": "#a6adc8",
    "accent": "#f9e2af",       # warm amber
    "accent2": "#fab387",      # peach
    "hole": "#313244",         # dark grey for holes
    "hole_border": "#6c7086",
    "alloc": "#f9e2af",        # amber for allocated
    "alloc_border": "#fab387",
    "text_hole": "#a6adc8",
    "text_alloc": "#1e1e2e",
    "success": "#a6e3a1",
    "error": "#f38ba8",
    "warn": "#f9e2af",
}


class MemoryAllocatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Memory Allocation Simulator – Segmentation")
        self.root.geometry("1400x850")
        self.root.configure(bg=COLORS["bg_dark"])

        self.manager: MemoryManager = None
        self.processes_input: List[Process] = []

        # Configure ttk styles for dark theme
        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # General
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["fg_main"], font=("Segoe UI", 10))
        style.configure("TButton",
                        background=COLORS["accent"],
                        foreground=COLORS["text_alloc"],
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0,
                        focusthickness=0)
        style.map("TButton",
                  background=[("active", COLORS["accent2"]), ("pressed", COLORS["accent2"])])

        style.configure("TRadiobutton",
                        background=COLORS["bg_dark"],
                        foreground=COLORS["fg_main"],
                        font=("Segoe UI", 10))
        style.configure("TCombobox",
                        fieldbackground=COLORS["bg_input"],
                        background=COLORS["bg_input"],
                        foreground=COLORS["fg_main"])

        # Custom label frames
        style.configure("Card.TLabelframe",
                        background=COLORS["bg_card"],
                        foreground=COLORS["accent"],
                        borderwidth=2,
                        relief="solid")
        style.configure("Card.TLabelframe.Label",
                        background=COLORS["bg_card"],
                        foreground=COLORS["accent"],
                        font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg=COLORS["bg_dark"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===== TOP SECTION: Controls (horizontal) =====
        controls_frame = tk.Frame(main_container, bg=COLORS["bg_dark"])
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # -- Memory Setup Card --
        setup_card = ttk.LabelFrame(controls_frame, text=" Memory Setup ", style="Card.TLabelframe", padding=12)
        setup_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(setup_card, text="Total Memory (K):", bg=COLORS["bg_card"], fg=COLORS["fg_main"], font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.total_size_var = tk.IntVar(value=1000)
        tk.Entry(setup_card, textvariable=self.total_size_var, width=12,
                 bg=COLORS["bg_input"], fg=COLORS["fg_main"],
                 insertbackground=COLORS["fg_main"],
                 relief="flat", font=("Consolas", 10)).grid(row=0, column=1, padx=5, pady=2)

        tk.Label(setup_card, text="Holes (start,size):", bg=COLORS["bg_card"], fg=COLORS["fg_dim"], font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.NW, pady=(8,0))
        self.holes_text = tk.Text(setup_card, width=22, height=4,
                                  bg=COLORS["bg_input"], fg=COLORS["fg_main"],
                                  insertbackground=COLORS["fg_main"],
                                  relief="flat", font=("Consolas", 9))
        self.holes_text.grid(row=1, column=1, padx=5, pady=(8,0))
        self.holes_text.insert(tk.END, "0,300\n400,250\n700,200")

        tk.Button(setup_card, text="Initialize Memory", command=self._init_memory,
                  bg=COLORS["accent"], fg=COLORS["text_alloc"],
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  activebackground=COLORS["accent2"], cursor="hand2").grid(row=2, column=0, columnspan=2, pady=(10,0), sticky=tk.EW)

        # -- Method Card --
        method_card = ttk.LabelFrame(controls_frame, text=" Allocation Method ", style="Card.TLabelframe", padding=12)
        method_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.method_var = tk.StringVar(value="first_fit")
        tk.Radiobutton(method_card, text="First-Fit", variable=self.method_var, value="first_fit",
                       bg=COLORS["bg_card"], fg=COLORS["fg_main"],
                       selectcolor=COLORS["accent"], font=("Segoe UI", 10),
                       activebackground=COLORS["bg_card"], activeforeground=COLORS["accent"]).pack(anchor=tk.W, pady=3)
        tk.Radiobutton(method_card, text="Best-Fit", variable=self.method_var, value="best_fit",
                       bg=COLORS["bg_card"], fg=COLORS["fg_main"],
                       selectcolor=COLORS["accent"], font=("Segoe UI", 10),
                       activebackground=COLORS["bg_card"], activeforeground=COLORS["accent"]).pack(anchor=tk.W, pady=3)

        tk.Button(method_card, text="Set Method", command=self._set_method,
                  bg=COLORS["accent"], fg=COLORS["text_alloc"],
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  activebackground=COLORS["accent2"], cursor="hand2").pack(fill=tk.X, pady=(12,0))

        # -- Process Input Card --
        proc_card = ttk.LabelFrame(controls_frame, text=" Process Input ", style="Card.TLabelframe", padding=12)
        proc_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(proc_card, text="Process Name:", bg=COLORS["bg_card"], fg=COLORS["fg_main"], font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.proc_name_var = tk.StringVar()
        tk.Entry(proc_card, textvariable=self.proc_name_var, width=15,
                 bg=COLORS["bg_input"], fg=COLORS["fg_main"],
                 insertbackground=COLORS["fg_main"],
                 relief="flat", font=("Consolas", 10)).grid(row=0, column=1, padx=5, pady=2)

        tk.Label(proc_card, text="Segments (name:size):", bg=COLORS["bg_card"], fg=COLORS["fg_dim"], font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.NW, pady=(8,0))
        self.segments_text = tk.Text(proc_card, width=24, height=4,
                                     bg=COLORS["bg_input"], fg=COLORS["fg_main"],
                                     insertbackground=COLORS["fg_main"],
                                     relief="flat", font=("Consolas", 9))
        self.segments_text.grid(row=1, column=1, padx=5, pady=(8,0))
        self.segments_text.insert(tk.END, "Code:100\nData:120\nStack:90")

        btn_frame = tk.Frame(proc_card, bg=COLORS["bg_card"])
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10,0), sticky=tk.EW)
        tk.Button(btn_frame, text="Add Process", command=self._add_process,
                  bg=COLORS["accent"], fg=COLORS["text_alloc"],
                  font=("Segoe UI", 9, "bold"), relief="flat",
                  activebackground=COLORS["accent2"], cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,3))
        tk.Button(btn_frame, text="Allocate", command=self._allocate_process,
                  bg="#a6e3a1", fg=COLORS["text_alloc"],
                  font=("Segoe UI", 9, "bold"), relief="flat",
                  activebackground="#81c995", cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        # -- Deallocation Card --
        dealloc_card = ttk.LabelFrame(controls_frame, text=" Deallocation ", style="Card.TLabelframe", padding=12)
        dealloc_card.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(dealloc_card, text="Process:", bg=COLORS["bg_card"], fg=COLORS["fg_main"], font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.dealloc_var = tk.StringVar()
        self.dealloc_combo = ttk.Combobox(dealloc_card, textvariable=self.dealloc_var, state="readonly", width=14, font=("Consolas", 10))
        self.dealloc_combo.grid(row=0, column=1, padx=5, pady=2)

        tk.Button(dealloc_card, text="Deallocate", command=self._deallocate_process,
                  bg="#f38ba8", fg=COLORS["text_alloc"],
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  activebackground="#f27788", cursor="hand2").grid(row=1, column=0, columnspan=2, pady=(12,0), sticky=tk.EW)

        # ===== BOTTOM SECTION: Visualization (horizontal split) =====
        bottom_frame = tk.Frame(main_container, bg=COLORS["bg_dark"])
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # -- Left: Memory Layout Canvas --
        canvas_card = ttk.LabelFrame(bottom_frame, text=" Memory Layout ", style="Card.TLabelframe", padding=10)
        canvas_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(canvas_card, bg=COLORS["bg_dark"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # -- Right: Tables & History --
        right_frame = tk.Frame(bottom_frame, bg=COLORS["bg_dark"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        right_frame.configure(width=500)
        right_frame.pack_propagate(False)

        # Tables
        table_card = ttk.LabelFrame(right_frame, text=" Segment Tables & Partitions ", style="Card.TLabelframe", padding=8)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.table_text = scrolledtext.ScrolledText(
            table_card, width=55, height=14,
            bg=COLORS["bg_input"], fg=COLORS["fg_main"],
            insertbackground=COLORS["fg_main"],
            font=("Consolas", 10),
            relief="flat", state=tk.DISABLED
        )
        self.table_text.pack(fill=tk.BOTH, expand=True)

        # History
        hist_card = ttk.LabelFrame(right_frame, text=" Operation History ", style="Card.TLabelframe", padding=8)
        hist_card.pack(fill=tk.BOTH, expand=True)

        self.history_text = scrolledtext.ScrolledText(
            hist_card, width=55, height=10,
            bg=COLORS["bg_input"], fg=COLORS["fg_dim"],
            insertbackground=COLORS["fg_main"],
            font=("Consolas", 9),
            relief="flat", state=tk.DISABLED
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)

    def _init_memory(self):
        try:
            total = self.total_size_var.get()
            self.manager = MemoryManager(total)
            self.manager.set_allocation_method(self.method_var.get())

            holes_str = self.holes_text.get("1.0", tk.END).strip()
            for line in holes_str.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                start = int(parts[0].strip())
                size = int(parts[1].strip())
                self.manager.add_hole(start, size)

            self.processes_input.clear()
            self._update_ui()
            messagebox.showinfo("Success", "Memory initialized successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _set_method(self):
        if self.manager:
            self.manager.set_allocation_method(self.method_var.get())
            messagebox.showinfo("Success", f"Method set to {self.method_var.get().replace('_', '-').title()}")
        else:
            messagebox.showwarning("Warning", "Initialize memory first!")

    def _add_process(self):
        name = self.proc_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Process name required")
            return

        if any(p.name == name for p in self.processes_input):
            messagebox.showerror("Error", f"Process {name} already exists in input list.")
            return

        segs_str = self.segments_text.get("1.0", tk.END).strip()
        segments = []
        for line in segs_str.splitlines():
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                sname, ssize = line.split(':', 1)
            elif '=' in line:
                sname, ssize = line.split('=', 1)
            else:
                sname, ssize = line.split(',')
            segments.append(Segment(sname.strip(), int(ssize.strip())))

        proc = Process(name, segments)
        self.processes_input.append(proc)
        self._update_dealloc_combo()
        messagebox.showinfo("Success", f"Process {name} added with {len(segments)} segments.")

    def _allocate_process(self):
        if not self.manager:
            messagebox.showwarning("Warning", "Initialize memory first!")
            return

        name = self.proc_name_var.get().strip()
        proc = next((p for p in self.processes_input if p.name == name), None)
        if not proc:
            messagebox.showerror("Error", f"Process {name} not found. Add it first.")
            return

        success = self.manager.allocate_process(proc)
        self._update_ui()
        if not success:
            messagebox.showwarning("Allocation Failed", f"Could not allocate process {name}.")

    def _deallocate_process(self):
        if not self.manager:
            return
        name = self.dealloc_var.get()
        if not name:
            return
        self.manager.deallocate_process(name)
        self._update_ui()

    def _update_dealloc_combo(self):
        names = [p.name for p in self.processes_input]
        self.dealloc_combo['values'] = names
        if names and not self.dealloc_var.get():
            self.dealloc_var.set(names[0])

    def _update_ui(self):
        self._draw_memory()
        self._update_tables()
        self._update_history()
        self._update_dealloc_combo()

    def _draw_memory(self):
        self.canvas.delete("all")
        if not self.manager:
            return

        # Get canvas dimensions
        self.canvas.update_idletasks()
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)

        margin_x = 40
        margin_y = 30
        bar_height = ch - 2 * margin_y
        bar_width = 140

        layout = self.manager.get_memory_layout()
        if not layout:
            self.canvas.create_text(cw//2, ch//2, text="No memory layout to display",
                                    fill=COLORS["fg_dim"], font=("Segoe UI", 14))
            return

        total = self.manager.total_size

        # Draw scale line on the left
        scale_x = margin_x + bar_width + 20
        self.canvas.create_line(scale_x, margin_y, scale_x, margin_y + bar_height,
                                fill=COLORS["fg_dim"], width=1)

        # Tick marks every 100K or adaptive
        tick_step = 100 if total <= 1000 else 200
        for addr in range(0, total + 1, tick_step):
            y = margin_y + (addr / total) * bar_height
            self.canvas.create_line(scale_x - 5, y, scale_x + 5, y, fill=COLORS["fg_dim"])
            self.canvas.create_text(scale_x + 25, y, text=str(addr),
                                    fill=COLORS["fg_dim"], font=("Consolas", 9), anchor=tk.W)

        # Draw memory bar (horizontal orientation: segments stacked vertically)
        current_y = margin_y
        for block in layout:
            bh = (block['size'] / total) * bar_height

            if block['type'] == 'hole':
                fill_color = COLORS["hole"]
                border_color = COLORS["hole_border"]
                text_color = COLORS["text_hole"]
            else:
                fill_color = COLORS["alloc"]
                border_color = COLORS["alloc_border"]
                text_color = COLORS["text_alloc"]

            # Draw block
            self.canvas.create_rectangle(
                margin_x, current_y,
                margin_x + bar_width, current_y + bh,
                fill=fill_color, outline=border_color, width=2
            )

            # Draw label (truncate if too small)
            if bh > 20:
                label = block['label'].replace("\n", "\n")
                lines = label.split("\n")
                # Center text
                mid_y = current_y + bh / 2
                offset = -(len(lines) * 8) / 2
                for i, line in enumerate(lines):
                    self.canvas.create_text(
                        margin_x + bar_width / 2,
                        mid_y + offset + i * 16,
                        text=line,
                        fill=text_color,
                        font=("Segoe UI", 8, "bold" if block['type'] == 'allocated' else "normal")
                    )

            current_y += bh

        # Title
        self.canvas.create_text(
            margin_x + bar_width / 2, margin_y - 15,
            text=f"Physical Memory (0 – {total-1})",
            fill=COLORS["accent"], font=("Segoe UI", 11, "bold")
        )

        # Legend
        legend_x = margin_x + bar_width + 80
        legend_y = margin_y
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + 15, legend_y + 15,
                                     fill=COLORS["alloc"], outline=COLORS["alloc_border"])
        self.canvas.create_text(legend_x + 22, legend_y + 7, text="Allocated", fill=COLORS["fg_main"],
                                font=("Segoe UI", 9), anchor=tk.W)
        self.canvas.create_rectangle(legend_x, legend_y + 25, legend_x + 15, legend_y + 40,
                                     fill=COLORS["hole"], outline=COLORS["hole_border"])
        self.canvas.create_text(legend_x + 22, legend_y + 32, text="Free Hole", fill=COLORS["fg_main"],
                                font=("Segoe UI", 9), anchor=tk.W)

    def _update_tables(self):
        self.table_text.configure(state=tk.NORMAL)
        self.table_text.delete("1.0", tk.END)

        if not self.manager:
            self.table_text.configure(state=tk.DISABLED)
            return

        # Segment Tables
        for name, proc in self.manager.processes.items():
            if not proc.is_allocated:
                continue
            table = self.manager.get_segment_table(name)
            self.table_text.insert(tk.END, f"┌─ Process {name} Segment Table ")
            self.table_text.insert(tk.END, "─" * (40 - len(name)) + "┐\n")
            self.table_text.insert(tk.END, f"│ {'Segment':<12} {'Base':<10} {'Limit':<10} │\n")
            self.table_text.insert(tk.END, f"├{'─'*38}┤\n")
            for entry in table:
                self.table_text.insert(tk.END, f"│ {entry['segment']:<12} {entry['base']:<10} {entry['limit']:<10} │\n")
            self.table_text.insert(tk.END, f"└{'─'*38}┘\n\n")

        # Free Holes
        self.table_text.insert(tk.END, f"┌─ Free Holes Table {'─'*21}┐\n")
        self.table_text.insert(tk.END, f"│ {'Start':<10} {'Size':<10} {'End':<10} │\n")
        self.table_text.insert(tk.END, f"├{'─'*38}┤\n")
        for hole in self.manager.holes:
            self.table_text.insert(tk.END, f"│ {hole.start:<10} {hole.size:<10} {hole.end:<10} │\n")
        self.table_text.insert(tk.END, f"└{'─'*38}┘\n\n")

        # Allocated Partitions
        self.table_text.insert(tk.END, f"┌─ Allocated Partitions Table {'─'*13}┐\n")
        self.table_text.insert(tk.END, f"│ {'Process':<10} {'Segment':<12} {'Start':<8} {'Size':<6} │\n")
        self.table_text.insert(tk.END, f"├{'─'*38}┤\n")
        for alloc in self.manager.allocated:
            self.table_text.insert(tk.END, f"│ {alloc.process_name:<10} {alloc.segment_name:<12} {alloc.start:<8} {alloc.size:<6} │\n")
        self.table_text.insert(tk.END, f"└{'─'*38}┘\n")

        self.table_text.configure(state=tk.DISABLED)

    def _update_history(self):
        self.history_text.configure(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        if self.manager:
            for line in self.manager.history:
                # Color-code lines
                if "does not fit" in line or "Error" in line:
                    tag = "error"
                elif "Allocated" in line:
                    tag = "alloc"
                elif "Deallocated" in line:
                    tag = "dealloc"
                else:
                    tag = "normal"

                self.history_text.insert(tk.END, line + "\n", tag)

        self.history_text.tag_config("error", foreground=COLORS["error"])
        self.history_text.tag_config("alloc", foreground=COLORS["success"])
        self.history_text.tag_config("dealloc", foreground=COLORS["accent"])
        self.history_text.tag_config("normal", foreground=COLORS["fg_dim"])
        self.history_text.configure(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = MemoryAllocatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
