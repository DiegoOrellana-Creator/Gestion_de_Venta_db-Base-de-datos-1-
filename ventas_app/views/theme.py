"""
Tema visual y widgets reutilizables para toda la app.
Paleta: fondo oscuro carbón + acento verde esmeralda.
"""
import tkinter as tk
from tkinter import ttk

# ── PALETA ────────────────────────────────────────────────────
C = {
    "bg":        "#0F1117",   # fondo principal
    "panel":     "#1A1D27",   # paneles / sidebar
    "card":      "#22263A",   # tarjetas
    "border":    "#2E3350",   # bordes
    "accent":    "#00C896",   # verde esmeralda
    "accent2":   "#0096FF",   # azul info
    "danger":    "#FF4D6A",   # rojo
    "warning":   "#FFB830",   # naranja
    "text":      "#E8ECF5",   # texto principal
    "muted":     "#6B7399",   # texto secundario
    "row_odd":   "#1E2236",
    "row_even":  "#181B2C",
    "select":    "#003D2B",   # selección tabla
}

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_HEAD   = ("Segoe UI", 12, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)


def apply_theme(root: tk.Tk):
    """Aplica el tema global a ttk y tk."""
    root.configure(bg=C["bg"])
    style = ttk.Style(root)
    style.theme_use("clam")

    # Frame / LabelFrame
    style.configure("TFrame",      background=C["bg"])
    style.configure("Card.TFrame", background=C["card"])
    style.configure("Panel.TFrame",background=C["panel"])
    style.configure("TLabelframe", background=C["panel"], foreground=C["text"],
                    bordercolor=C["border"], relief="flat")
    style.configure("TLabelframe.Label", background=C["panel"],
                    foreground=C["accent"], font=FONT_HEAD)

    # Label
    style.configure("TLabel",       background=C["bg"],    foreground=C["text"], font=FONT_BODY)
    style.configure("Muted.TLabel", background=C["bg"],    foreground=C["muted"],font=FONT_SMALL)
    style.configure("Title.TLabel", background=C["bg"],    foreground=C["text"], font=FONT_TITLE)
    style.configure("Head.TLabel",  background=C["panel"], foreground=C["text"], font=FONT_HEAD)
    style.configure("Card.TLabel",  background=C["card"],  foreground=C["text"], font=FONT_BODY)
    style.configure("Accent.TLabel",background=C["card"],  foreground=C["accent"],font=("Segoe UI",22,"bold"))

    # Button
    for name, bg, fg in [
        ("Accent.TButton", C["accent"],  C["bg"]),
        ("Danger.TButton", C["danger"],  "#fff"),
        ("Info.TButton",   C["accent2"], "#fff"),
        ("Muted.TButton",  C["border"],  C["text"]),
    ]:
        style.configure(name, background=bg, foreground=fg,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat", borderwidth=0, padding=(14, 8))
        style.map(name,
                  background=[("active", _darken(bg)), ("pressed", _darken(bg, 0.15))],
                  relief=[("pressed", "flat")])

    # Entry
    style.configure("TEntry", fieldbackground=C["card"], foreground=C["text"],
                    bordercolor=C["border"], relief="flat",
                    insertcolor=C["accent"], padding=6, font=FONT_BODY)
    style.map("TEntry", bordercolor=[("focus", C["accent"])])

    # Combobox
    style.configure("TCombobox", fieldbackground=C["card"], foreground=C["text"],
                    background=C["card"], arrowcolor=C["accent"],
                    bordercolor=C["border"], padding=6, font=FONT_BODY)
    style.map("TCombobox",
              fieldbackground=[("readonly", C["card"])],
              selectbackground=[("readonly", C["card"])],
              selectforeground=[("readonly", C["text"])])

    # Treeview
    style.configure("Treeview",
                    background=C["row_even"], fieldbackground=C["row_even"],
                    foreground=C["text"], rowheight=32, font=FONT_BODY,
                    bordercolor=C["border"], relief="flat")
    style.configure("Treeview.Heading",
                    background=C["panel"], foreground=C["accent"],
                    font=("Segoe UI", 9, "bold"), relief="flat",
                    bordercolor=C["border"])
    style.map("Treeview",
              background=[("selected", C["select"])],
              foreground=[("selected", C["accent"])])

    # Scrollbar
    style.configure("TScrollbar", background=C["panel"], troughcolor=C["bg"],
                    arrowcolor=C["muted"], bordercolor=C["bg"], relief="flat")

    # Notebook
    style.configure("TNotebook",     background=C["bg"],    bordercolor=C["border"])
    style.configure("TNotebook.Tab", background=C["panel"], foreground=C["muted"],
                    padding=(16, 8), font=("Segoe UI", 10))
    style.map("TNotebook.Tab",
              background=[("selected", C["bg"])],
              foreground=[("selected", C["accent"])],
              expand=[("selected", [1, 1, 1, 0])])

    # Separator
    style.configure("TSeparator", background=C["border"])

    # Spinbox
    style.configure("TSpinbox", fieldbackground=C["card"], foreground=C["text"],
                    background=C["card"], arrowcolor=C["accent"],
                    bordercolor=C["border"], padding=6, font=FONT_BODY)


def _darken(hex_color: str, factor=0.1) -> str:
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


# ── WIDGETS REUTILIZABLES ─────────────────────────────────────

class ScrolledTree(tk.Frame):
    """Treeview con scrollbars vertical y horizontal."""
    def __init__(self, parent, columns: list, **kw):
        super().__init__(parent, bg=C["bg"])
        self.tree = ttk.Treeview(self, columns=columns, show="headings", **kw)
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self._stripe()

    def _stripe(self):
        self.tree.tag_configure("odd",  background=C["row_odd"])
        self.tree.tag_configure("even", background=C["row_even"])

    def set_columns(self, cols_config: list):
        """cols_config: [{'text':..,'width':..,'anchor':..}, ...]"""
        for i, (col, cfg) in enumerate(zip(self.tree['columns'], cols_config)):
            self.tree.heading(col, text=cfg.get('text', col))
            self.tree.column(col, width=cfg.get('width', 120),
                             anchor=cfg.get('anchor', 'w'), stretch=cfg.get('stretch', True))

    def load(self, rows: list):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(i), values=row, tags=(tag,))

    def load_with_ids(self, rows: list):
        """rows: [(iid, values_tuple), ...]"""
        self.tree.delete(*self.tree.get_children())
        for i, (iid, vals) in enumerate(rows):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=str(iid), values=vals, tags=(tag,))

    def selected_iid(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def bind_select(self, callback):
        self.tree.bind("<<TreeviewSelect>>", callback)

    def bind_double(self, callback):
        self.tree.bind("<Double-1>", callback)


class LabeledEntry(tk.Frame):
    """Label + Entry en columna."""
    def __init__(self, parent, label: str, **entry_kw):
        super().__init__(parent, bg=C["bg"])
        ttk.Label(self, text=label, style="Muted.TLabel").pack(anchor="w")
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var, **entry_kw)
        self.entry.pack(fill="x", pady=(2, 0))

    def get(self): return self.var.get()
    def set(self, v): self.var.set(v)
    def clear(self): self.var.set("")


class LabeledCombo(tk.Frame):
    """Label + Combobox en columna."""
    def __init__(self, parent, label: str, values=(), **kw):
        super().__init__(parent, bg=C["bg"])
        ttk.Label(self, text=label, style="Muted.TLabel").pack(anchor="w")
        self.var = tk.StringVar()
        self.combo = ttk.Combobox(self, textvariable=self.var,
                                  values=values, state="readonly", **kw)
        self.combo.pack(fill="x", pady=(2, 0))

    def get(self): return self.var.get()
    def set(self, v): self.var.set(v)
    def bind_change(self, cb): self.combo.bind("<<ComboboxSelected>>", cb)


class StatCard(tk.Frame):
    """Tarjeta de métrica para el dashboard."""
    def __init__(self, parent, title: str, value: str, color=None):
        super().__init__(parent, bg=C["card"], padx=20, pady=16)
        color = color or C["accent"]
        ttk.Label(self, text=title, background=C["card"],
                  foreground=C["muted"], font=FONT_SMALL).pack(anchor="w")
        ttk.Label(self, text=value, background=C["card"],
                  foreground=color, font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(4, 0))

    def update_value(self, value: str, color=None):
        for w in self.winfo_children():
            if isinstance(w, ttk.Label) and w.cget("font") == str(("Segoe UI", 24, "bold")):
                w.config(text=value)
                if color: w.config(foreground=color)
                break


def sidebar_btn(parent, text: str, icon: str, command):
    """Botón de barra lateral."""
    f = tk.Frame(parent, bg=C["panel"], cursor="hand2")
    tk.Label(f, text=f" {icon}  {text}", bg=C["panel"],
             fg=C["muted"], font=("Segoe UI", 11),
             anchor="w", padx=12, pady=10).pack(fill="x")

    def on_enter(e):
        for w in f.winfo_children(): w.config(bg=C["card"])
        f.config(bg=C["card"])
    def on_leave(e):
        for w in f.winfo_children(): w.config(bg=C["panel"])
        f.config(bg=C["panel"])
    def on_click(e): command()

    f.bind("<Enter>", on_enter); f.bind("<Leave>", on_leave); f.bind("<Button-1>", on_click)
    for w in f.winfo_children():
        w.bind("<Enter>", on_enter); w.bind("<Leave>", on_leave); w.bind("<Button-1>", on_click)
    return f


def active_sidebar_btn(parent, text: str, icon: str, command):
    """Botón de barra lateral activo."""
    f = tk.Frame(parent, bg=C["accent"], cursor="hand2")
    tk.Label(f, text=f" {icon}  {text}", bg=C["accent"],
             fg=C["bg"], font=("Segoe UI", 11, "bold"),
             anchor="w", padx=12, pady=10).pack(fill="x")
    f.bind("<Button-1>", lambda e: command())
    for w in f.winfo_children(): w.bind("<Button-1>", lambda e: command())
    return f
