import tkinter as tk
from tkinter import ttk
from views.theme import C, FONT_HEAD, ScrolledTree
from controllers.controllers import ProductoController


class StockView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._build()
        self.refresh()

    def _build(self):
        ttk.Label(self, text="Inventario / Stock", style="Title.TLabel").pack(anchor="w", padx=28, pady=(24,4))
        ttk.Label(self, text="Distribución de productos por tienda y almacén", style="Muted.TLabel").pack(anchor="w", padx=28)
        ttk.Separator(self).pack(fill="x", padx=28, pady=12)

        toolbar = tk.Frame(self, bg=C["bg"])
        toolbar.pack(fill="x", padx=28, pady=(0,8))
        ttk.Button(toolbar, text="↻ Actualizar", style="Muted.TButton",
                   command=self.refresh).pack(side="right")

        frame = tk.Frame(self, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=28, pady=(0,20))

        self.tree = ScrolledTree(frame, columns=("ubicacion","producto","cantidad","fecha"))
        self.tree.set_columns([
            {"text":"Ubicación",    "width":200},
            {"text":"Producto",     "width":250},
            {"text":"Cantidad",     "width":90, "anchor":"center"},
            {"text":"Última entrada","width":140},
        ])
        self.tree.pack(fill="both", expand=True)

        # Alerta stock bajo
        self.alerta_frame = tk.Frame(self, bg=C["warning"])
        self.lbl_alerta = tk.Label(self.alerta_frame, text="", bg=C["warning"],
                                    fg=C["bg"], font=("Segoe UI", 10, "bold"), pady=6)
        self.lbl_alerta.pack(fill="x", padx=20)

    def refresh(self):
        stocks = ProductoController.listar_stock()
        self.tree.tree.delete(*self.tree.tree.get_children())
        bajos = []
        for i, s in enumerate(stocks):
            tag = "odd" if i%2 else "even"
            if s.cantidad <= 5:
                tag = "bajo"
                self.tree.tree.tag_configure("bajo", foreground=C["warning"])
                bajos.append(s.producto_nombre)
            fecha = s.fecha_ingreso[:10] if s.fecha_ingreso else ""
            self.tree.tree.insert("", "end", iid=str(i), tags=(tag,),
                values=(s.ubicacion_nombre, s.producto_nombre, s.cantidad, fecha))
        if bajos:
            self.alerta_frame.pack(fill="x", padx=28, pady=(0,12))
            self.lbl_alerta.config(text=f"⚠ Stock bajo (≤5 unidades): {', '.join(set(bajos))}")
        else:
            self.alerta_frame.pack_forget()
