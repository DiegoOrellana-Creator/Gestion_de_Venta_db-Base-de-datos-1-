import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import C, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_MONO, ScrolledTree, LabeledCombo
from controllers.controllers import VentaController, ProductoController, ClienteController, VendedorController


class NuevaVentaView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._carrito = []          # list of dicts
        self._productos_cache = []
        self._build()
        self._load_combos()

    # ── CONSTRUCCIÓN UI ───────────────────────────────────────
    def _build(self):
        ttk.Label(self, text="Nueva Venta", style="Title.TLabel").pack(anchor="w", padx=28, pady=(24,4))
        ttk.Label(self, text="Registra una nueva transacción", style="Muted.TLabel").pack(anchor="w", padx=28)
        ttk.Separator(self).pack(fill="x", padx=28, pady=12)

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)

        # ─── Panel izquierdo ──────────────────────────────────
        left = tk.Frame(body, bg=C["panel"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(left, text="  Datos de la venta", bg=C["panel"], fg=C["text"],
                 font=FONT_HEAD, pady=12).pack(anchor="w")

        form = tk.Frame(left, bg=C["panel"])
        form.pack(fill="x", padx=14, pady=4)
        form.columnconfigure(0, weight=1)

        self.combo_cliente  = LabeledCombo(form, "Cliente")
        self.combo_cliente.grid(row=0, column=0, sticky="ew", pady=5)

        self.combo_vendedor = LabeledCombo(form, "Vendedor")
        self.combo_vendedor.grid(row=1, column=0, sticky="ew", pady=5)

        self.combo_metodo   = LabeledCombo(form, "Método de pago",
                                            values=["Efectivo", "Tarjeta", "QR"])
        self.combo_metodo.combo.current(0)
        self.combo_metodo.grid(row=2, column=0, sticky="ew", pady=5)

        ttk.Separator(left).pack(fill="x", padx=10, pady=10)
        tk.Label(left, text="  Agregar producto", bg=C["panel"], fg=C["text"],
                 font=FONT_HEAD).pack(anchor="w", padx=4)

        search_f = tk.Frame(left, bg=C["panel"])
        search_f.pack(fill="x", padx=14, pady=6)
        self.var_buscar = tk.StringVar()
        self.var_buscar.trace_add("write", self._on_search)
        ttk.Label(search_f, text="Buscar producto", style="Muted.TLabel").pack(anchor="w")
        ttk.Entry(search_f, textvariable=self.var_buscar).pack(fill="x", pady=2)

        self.tree_prods = ScrolledTree(left, columns=("nombre", "tipo", "precio", "descuento", "stock"))
        self.tree_prods.set_columns([
            {"text": "Producto",   "width": 150},
            {"text": "Tipo",       "width": 70},
            {"text": "Precio",     "width": 70, "anchor": "e"},
            {"text": "Desc.%",     "width": 60, "anchor": "center"},
            {"text": "Stock",      "width": 55, "anchor": "e"},
        ])
        self.tree_prods.pack(fill="both", expand=True, padx=8, pady=4)
        self.tree_prods.bind_double(self._add_from_tree)

        qty_f = tk.Frame(left, bg=C["panel"])
        qty_f.pack(fill="x", padx=14, pady=6)
        ttk.Label(qty_f, text="Cantidad:", background=C["panel"],
                  foreground=C["muted"], font=FONT_SMALL).pack(side="left")
        self.spin_qty = ttk.Spinbox(qty_f, from_=1, to=9999, width=6)
        self.spin_qty.set(1)
        self.spin_qty.pack(side="left", padx=6)
        ttk.Button(qty_f, text="＋ Agregar al carrito",
                   style="Accent.TButton", command=self._add_to_cart).pack(side="left", padx=6)

        # ─── Panel derecho: carrito ───────────────────────────
        right = tk.Frame(body, bg=C["panel"])
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="  Carrito", bg=C["panel"], fg=C["text"],
                 font=FONT_HEAD, pady=12).pack(anchor="w")

        self.tree_carrito = ScrolledTree(right, columns=("producto","qty","precio","subtotal"))
        self.tree_carrito.set_columns([
            {"text": "Producto",   "width": 200},
            {"text": "Cant.",      "width": 50,  "anchor": "center"},
            {"text": "P. Unit.",   "width": 80,  "anchor": "e"},
            {"text": "Subtotal",   "width": 90,  "anchor": "e"},
        ])
        # Contenedor interno para el área expandible (evitar mezclar pack/grid en `right`)
        content = tk.Frame(right, bg=C["panel"]) ; content.pack(fill="both", expand=True, padx=8, pady=4)
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        # crear tree dentro del content
        self.tree_carrito = ScrolledTree(content, columns=("producto","qty","precio","subtotal"))
        self.tree_carrito.set_columns([
            {"text": "Producto",   "width": 200},
            {"text": "Cant.",      "width": 50,  "anchor": "center"},
            {"text": "P. Unit.",   "width": 80,  "anchor": "e"},
            {"text": "Subtotal",   "width": 90,  "anchor": "e"},
        ])
        self.tree_carrito.grid(row=0, column=0, sticky="nsew")

        btn_bar = tk.Frame(content, bg=C["panel"])
        btn_bar.grid(row=1, column=0, sticky="ew", pady=6)
        ttk.Button(btn_bar, text="✕ Quitar selección", style="Danger.TButton",
                   command=self._remove_item).pack(side="left")
        ttk.Button(btn_bar, text="🗑 Vaciar", style="Muted.TButton",
                   command=self._clear_cart).pack(side="left", padx=6)
        # Nuevo botón para guardar la venta directamente desde el carrito
        ttk.Button(btn_bar, text="💾 Guardar Venta", style="Accent.TButton",
                   command=self._confirmar_venta).pack(side="left", padx=6)

        # Total
        total_f = tk.Frame(content, bg=C["card"])
        total_f.grid(row=2, column=0, sticky="ew", pady=(4, 8))
        tk.Label(total_f, text="TOTAL", bg=C["card"], fg=C["muted"],
                 font=("Segoe UI", 11)).pack(side="left", padx=16, pady=12)
        self.lbl_total = tk.Label(total_f, text="Bs. 0.00", bg=C["card"],
                                   fg=C["accent"], font=("Segoe UI", 22, "bold"))
        self.lbl_total.pack(side="right", padx=16)

        # Footer fijo en `right` para que el botón siempre quede visible
        footer = tk.Frame(right, bg=C["panel"])
        footer.pack(fill="x", side="bottom", padx=8, pady=(6, 12))
        ttk.Button(footer, text="✔  Registrar Venta", style="Accent.TButton",
               command=self._confirmar_venta).pack(side="right", ipadx=8, ipady=6)

    # ── LÓGICA ────────────────────────────────────────────────
    def _load_combos(self):
        clientes  = ClienteController.listar()
        vendedores = VendedorController.listar()
        self._clientes_map  = {c.nombre: c.id for c in clientes}
        self._vendedores_map = {v.nombre: v.id for v in vendedores}
        self.combo_cliente.combo.config(values=list(self._clientes_map.keys()))
        self.combo_vendedor.combo.config(values=list(self._vendedores_map.keys()))
        if clientes:  self.combo_cliente.combo.current(0)
        if vendedores: self.combo_vendedor.combo.current(0)
        self._refresh_products()

    def _refresh_products(self, term=""):
        self._productos_cache = ProductoController.listar(term)
        rows = [(
            p.nombre,
            p.tipo_producto,
            f"Bs. {p.precio_con_descuento():.2f}",
            f"{p.descuento:.0f}%" if p.descuento else "—",
            p.stock_total
        ) for p in self._productos_cache]
        self.tree_prods.load(rows)

    def refresh(self):
        # recargar combos y productos al mostrar la vista
        try:
            self._load_combos()
        except Exception:
            pass
        try:
            self._refresh_products(self.var_buscar.get())
        except Exception:
            pass
        try:
            self._update_cart_view()
        except Exception:
            pass

    def _on_search(self, *_):
        self._refresh_products(self.var_buscar.get())

    def _add_from_tree(self, _event=None):
        self._add_to_cart()

    def _add_to_cart(self):
        iid = self.tree_prods.selected_iid()
        if iid is None:
            messagebox.showwarning("Selección", "Selecciona un producto de la lista.")
            return
        idx = int(iid)
        prod = self._productos_cache[idx]
        try:
            qty = int(self.spin_qty.get())
        except ValueError:
            qty = 1
        if qty < 1:
            return
        if prod.stock_total < qty:
            messagebox.showerror("Stock", f"Stock insuficiente ({prod.stock_total} disponibles).")
            return
        # Si ya está en carrito, sumar
        for item in self._carrito:
            if item['producto_id'] == prod.id_producto:
                item['cantidad'] += qty
                item['subtotal'] = round(item['cantidad'] * item['precio_unitario'], 2)
                self._update_cart_view()
                return
        self._carrito.append({
            'producto_id':    prod.id_producto,
            'nombre':         prod.nombre,
            'cantidad':       qty,
            'precio_unitario': prod.precio_con_descuento(),
            'subtotal':       round(qty * prod.precio_con_descuento(), 2),
        })
        self._update_cart_view()

    def _remove_item(self):
        iid = self.tree_carrito.selected_iid()
        if iid is None: return
        idx = int(iid)
        self._carrito.pop(idx)
        self._update_cart_view()

    def _clear_cart(self):
        self._carrito.clear()
        self._update_cart_view()

    def _update_cart_view(self):
        rows = [(i['nombre'], i['cantidad'],
                 f"Bs. {i['precio_unitario']:.2f}",
                 f"Bs. {i['subtotal']:.2f}") for i in self._carrito]
        self.tree_carrito.load(rows)
        total = sum(i['subtotal'] for i in self._carrito)
        self.lbl_total.config(text=f"Bs. {total:,.2f}")

    def _confirmar_venta(self):
        cliente_nombre  = self.combo_cliente.get()
        vendedor_nombre = self.combo_vendedor.get()
        metodo          = self.combo_metodo.get()
        if not cliente_nombre or not vendedor_nombre:
            messagebox.showerror("Datos incompletos", "Selecciona cliente y vendedor.")
            return
        if not self._carrito:
            messagebox.showwarning("Carrito vacío", "Agrega al menos un producto.")
            return
        cliente_id  = self._clientes_map[cliente_nombre]
        vendedor_id = self._vendedores_map[vendedor_nombre]
        ok, msg, venta = VentaController.crear_venta(
            cliente_id, vendedor_id, metodo, self._carrito)
        if ok:
            messagebox.showinfo("✔ Éxito", f"{msg}\nTotal: Bs. {venta.total:,.2f}")
            self._clear_cart()
            self._refresh_products()
        else:
            messagebox.showerror("Error", msg)
