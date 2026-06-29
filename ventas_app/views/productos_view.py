import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import C, FONT_HEAD, FONT_SMALL, ScrolledTree, LabeledEntry, LabeledCombo
from controllers.controllers import ProductoController


class ProductosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        ttk.Label(self, text="Catálogo de Productos", style="Title.TLabel").pack(anchor="w", padx=28, pady=(24,4))
        ttk.Label(self, text="Gestiona mochilas, calzados y pelotas", style="Muted.TLabel").pack(anchor="w", padx=28)
        ttk.Separator(self).pack(fill="x", padx=28, pady=12)

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=(0,20))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)

        # ─── Lista ───────────────────────────────────────────
        left = tk.Frame(body, bg=C["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        search_f = tk.Frame(left, bg=C["bg"])
        search_f.pack(fill="x", pady=(0,8))
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(search_f, textvariable=self.var_search, width=35).pack(side="left")
        ttk.Label(search_f, text=" ← Buscar por nombre o marca", style="Muted.TLabel").pack(side="left", padx=6)
        ttk.Button(search_f, text="↻", style="Muted.TButton", command=self.refresh).pack(side="right")

        self.tree = ScrolledTree(left, columns=("nombre","tipo","marca","precio","descuento","stock"))
        self.tree.set_columns([
            {"text": "Nombre",     "width": 180},
            {"text": "Tipo",       "width": 70},
            {"text": "Marca",      "width": 90},
            {"text": "Precio",     "width": 70,  "anchor":"e"},
            {"text": "Desc.%",     "width": 70,  "anchor":"center"},
            {"text": "Stock",      "width": 60,  "anchor":"e"},
        ])
        self.tree.pack(fill="both", expand=True)
        self.tree.bind_select(self._on_select)

        toolbar = tk.Frame(left, bg=C["bg"])
        toolbar.pack(fill="x", pady=(8,0))
        ttk.Button(toolbar, text="＋ Nuevo",          style="Accent.TButton", command=self._new).pack(side="left")
        ttk.Button(toolbar, text="✕ Desactivar",      style="Danger.TButton", command=self._delete).pack(side="left", padx=6)

        # ─── Formulario ──────────────────────────────────────
        right = tk.Frame(body, bg=C["panel"])
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="  Producto", bg=C["panel"], fg=C["text"],
                 font=FONT_HEAD, pady=12).pack(anchor="w")

        form = tk.Frame(right, bg=C["panel"])
        form.pack(fill="x", padx=16, pady=4)
        form.columnconfigure(0, weight=1)

        self.f_nombre = LabeledEntry(form, "Nombre del producto")
        self.f_nombre.configure(bg=C["panel"])
        self.f_nombre.grid(row=0, column=0, sticky="ew", pady=5)

        self.f_marca = LabeledEntry(form, "Marca")
        self.f_marca.configure(bg=C["panel"])
        self.f_marca.grid(row=1, column=0, sticky="ew", pady=5)

        self.f_precio = LabeledEntry(form, "Precio (Bs.)")
        self.f_precio.configure(bg=C["panel"])
        self.f_precio.grid(row=2, column=0, sticky="ew", pady=5)

        self.f_descuento = LabeledEntry(form, "Descuento (%)")
        self.f_descuento.configure(bg=C["panel"])
        self.f_descuento.grid(row=3, column=0, sticky="ew", pady=5)

        self.f_stock = LabeledEntry(form, "Stock inicial")
        self.f_stock.configure(bg=C["panel"])
        self.f_stock.grid(row=4, column=0, sticky="ew", pady=5)

        self.f_tipo = LabeledCombo(form, "Tipo", values=["Mochila","Calzado","Pelota"])
        self.f_tipo.configure(bg=C["panel"])
        self.f_tipo.combo.current(0)
        self.f_tipo.grid(row=5, column=0, sticky="ew", pady=5)

        ttk.Separator(right).pack(fill="x", padx=10, pady=10)

        btn_f = tk.Frame(right, bg=C["panel"])
        btn_f.pack(fill="x", padx=16, pady=(0,10))
        ttk.Button(btn_f, text="💾 Guardar", style="Accent.TButton", command=self._save).pack(fill="x", pady=3)
        ttk.Button(btn_f, text="✖ Cancelar", style="Muted.TButton", command=self._new).pack(fill="x")

        # Stock
        ttk.Separator(right).pack(fill="x", padx=10, pady=8)
        tk.Label(right, text="  Stock actual", bg=C["panel"], fg=C["text"],
                 font=FONT_HEAD).pack(anchor="w", padx=4)
        self.lbl_stock = tk.Label(right, text="—", bg=C["panel"], fg=C["accent"],
                                   font=("Segoe UI", 28, "bold"))
        self.lbl_stock.pack(anchor="w", padx=20)
        tk.Label(right, text="unidades en todas las ubicaciones", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=20)

    def refresh(self):
        term = self.var_search.get()
        prods = ProductoController.listar(term)
        rows = [(p.nombre, p.tipo_producto, p.marca,
                 f"Bs. {p.precio:.2f}",
                 f"{p.descuento:.0f}%" if p.descuento else "—",
                 p.stock_total) for p in prods]
        # Use id_producto as iid
        self.tree.tree.delete(*self.tree.tree.get_children())
        for i, (p, row) in enumerate(zip(prods, rows)):
            tag = "odd" if i % 2 else "even"
            self.tree.tree.insert("", "end", iid=p.id_producto, values=row, tags=(tag,))
        self._prods = prods

    def _on_select(self, _=None):
        iid = self.tree.selected_iid()
        if not iid: return
        from models.producto import Producto
        p = Producto.get_by_id(iid)
        if not p: return
        self._selected_id = p.id_producto
        self.f_nombre.set(p.nombre)
        self.f_marca.set(p.marca or "")
        self.f_precio.set(str(p.precio))
        self.f_descuento.set(str(int(p.descuento)) if p.descuento else "")
        self.f_stock.set(str(p.stock_total))
        self.f_tipo.set(p.tipo_producto)
        self.lbl_stock.config(text=str(p.stock_total))

    def _new(self):
        self._selected_id = None
        self.f_nombre.clear(); self.f_marca.clear()
        self.f_precio.clear(); self.f_descuento.clear(); self.f_stock.clear(); self.f_tipo.combo.current(0)
        self.lbl_stock.config(text="—")

    def _save(self):
        data = {
            'id_producto':  self._selected_id,
            'nombre':       self.f_nombre.get(),
            'marca':        self.f_marca.get(),
            'precio':       self.f_precio.get(),
            'descuento':    self.f_descuento.get(),
            'stock':        self.f_stock.get(),
            'tipo_producto': self.f_tipo.get(),
        }
        ok, msg = ProductoController.guardar(data)
        if ok:
            messagebox.showinfo("✔", msg)
            self._new(); self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def _delete(self):
        iid = self.tree.selected_iid()
        if not iid:
            messagebox.showwarning("Selección", "Selecciona un producto.")
            return
        if messagebox.askyesno("Desactivar", "¿Desactivar este producto?"):
            ok, msg = ProductoController.eliminar(iid)
            messagebox.showinfo("✔", msg) if ok else messagebox.showerror("Error", msg)
            self._new(); self.refresh()
