import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import C, FONT_HEAD, FONT_SMALL, ScrolledTree, LabeledEntry, LabeledCombo
from controllers.controllers import ClienteController, VendedorController


# ─────────────────────────────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────────────────────────────
class ClientesView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._sel = None
        self._build()
        self.refresh()

    def _build(self):
        ttk.Label(self, text="Clientes", style="Title.TLabel").pack(anchor="w", padx=28, pady=(24,4))
        ttk.Label(self, text="Gestiona los clientes registrados", style="Muted.TLabel").pack(anchor="w", padx=28)
        ttk.Separator(self).pack(fill="x", padx=28, pady=12)

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=(0,20))
        body.columnconfigure(0, weight=3); body.columnconfigure(1, weight=1)

        left = tk.Frame(body, bg=C["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        self.tree = ScrolledTree(left, columns=("nombre","email","telefono","puntos","credito"))
        self.tree.set_columns([
            {"text":"Nombre",   "width":180},
            {"text":"Email",    "width":180},
            {"text":"Teléfono", "width":120},
            {"text":"Puntos",   "width":70,  "anchor":"e"},
            {"text":"Crédito",  "width":80,  "anchor":"e"},
        ])
        self.tree.pack(fill="both", expand=True)
        self.tree.bind_select(self._on_select)

        toolbar = tk.Frame(left, bg=C["bg"])
        toolbar.pack(fill="x", pady=(8,0))
        ttk.Button(toolbar, text="↻ Actualizar", style="Muted.TButton", command=self.refresh).pack(side="right")
        ttk.Button(toolbar, text="✖ Eliminar", style="Danger.TButton", command=self._delete_selected).pack(side="right", padx=(8,0))

        # Formulario
        right = tk.Frame(body, bg=C["panel"])
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="  Cliente", bg=C["panel"], fg=C["text"], font=FONT_HEAD, pady=12).pack(anchor="w")

        form = tk.Frame(right, bg=C["panel"])
        form.pack(fill="x", padx=16, pady=4)
        form.columnconfigure(0, weight=1)

        self.f_nombre   = LabeledEntry(form, "Nombre completo"); self.f_nombre.configure(bg=C["panel"])
        self.f_nombre.grid(row=0, column=0, sticky="ew", pady=5)
        self.f_email    = LabeledEntry(form, "Email"); self.f_email.configure(bg=C["panel"])
        self.f_email.grid(row=1, column=0, sticky="ew", pady=5)
        self.f_telefono = LabeledEntry(form, "Teléfono"); self.f_telefono.configure(bg=C["panel"])
        self.f_telefono.grid(row=2, column=0, sticky="ew", pady=5)
        self.f_sexo     = LabeledCombo(form, "Sexo", values=["M","F","O"]); self.f_sexo.configure(bg=C["panel"])
        self.f_sexo.combo.current(0)
        self.f_sexo.grid(row=3, column=0, sticky="ew", pady=5)

        ttk.Separator(right).pack(fill="x", padx=10, pady=8)
        btn_f = tk.Frame(right, bg=C["panel"]); btn_f.pack(fill="x", padx=16, pady=(0,10))
        ttk.Button(btn_f, text="💾 Guardar nuevo", style="Accent.TButton", command=self._save).pack(fill="x", pady=3)
        ttk.Button(btn_f, text="✖ Limpiar",        style="Muted.TButton",  command=self._clear).pack(fill="x")

    def refresh(self):
        clientes = ClienteController.listar()
        self.tree.tree.delete(*self.tree.tree.get_children())
        for i, c in enumerate(clientes):
            tag = "odd" if i%2 else "even"
            self.tree.tree.insert("", "end", iid=c.id, tags=(tag,),
                values=(c.nombre, c.email, c.telefono, c.puntos, f"Bs. {c.credito:.2f}"))
        self._clientes = clientes

    def _on_select(self, _=None):
        iid = self.tree.selected_iid()
        if not iid: return
        c = next((x for x in self._clientes if x.id == iid), None)
        if not c: return
        self._sel = c
        self.f_nombre.set(c.nombre); self.f_email.set(c.email)
        self.f_telefono.set(c.telefono or "")

    def _clear(self):
        self._sel = None
        self.f_nombre.clear(); self.f_email.clear()
        self.f_telefono.clear(); self.f_sexo.combo.current(0)

    def _save(self):
        data = {'nombre': self.f_nombre.get(), 'email': self.f_email.get(),
                'telefono': self.f_telefono.get(), 'sexo': self.f_sexo.get(),
                'persona_id': self._sel.persona_id if self._sel else None,
                'rol_id':     self._sel.id if self._sel else None}
        ok, msg = ClienteController.guardar(data)
        messagebox.showinfo("✔", msg) if ok else messagebox.showerror("Error", msg)
        if ok: self._clear(); self.refresh()

    def _delete_selected(self):
        iid = self.tree.selected_iid()
        if not iid:
            messagebox.showwarning("Selecciona", "Selecciona un cliente para eliminar.")
            return
        c = next((x for x in self._clientes if x.id == iid), None)
        if not c:
            messagebox.showerror("Error", "Cliente no encontrado.")
            return
        if not messagebox.askyesno("Confirmar", f"Eliminar a {c.nombre}? Esta acción ocultará al cliente."):
            return
        ok, msg = ClienteController.eliminar(c.id)
        if ok:
            messagebox.showinfo("✔", msg)
            self.refresh()
            try:
                app = self.winfo_toplevel()
                nv = app._views.get('nueva_venta') if hasattr(app, '_views') else None
                if nv and hasattr(nv, '_load_combos'):
                    nv._load_combos()
            except Exception:
                pass
        else:
            messagebox.showerror("Error", msg)


# ─────────────────────────────────────────────────────────────
# VENDEDORES
# ─────────────────────────────────────────────────────────────
class VendedoresView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._sel = None
        self._build()
        self.refresh()

    def _build(self):
        ttk.Label(self, text="Vendedores", style="Title.TLabel").pack(anchor="w", padx=28, pady=(24,4))
        ttk.Label(self, text="Equipo de ventas registrado", style="Muted.TLabel").pack(anchor="w", padx=28)
        ttk.Separator(self).pack(fill="x", padx=28, pady=12)

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=(0,20))
        body.columnconfigure(0, weight=3); body.columnconfigure(1, weight=1)

        left = tk.Frame(body, bg=C["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        self.tree = ScrolledTree(left, columns=("nombre","email","codigo","comision"))
        self.tree.set_columns([
            {"text":"Nombre",   "width":180},
            {"text":"Email",    "width":180},
            {"text":"Código",   "width":90},
            {"text":"Comisión", "width":80, "anchor":"e"},
        ])
        self.tree.pack(fill="both", expand=True)
        self.tree.bind_select(self._on_select)
        ttk.Button(left, text="↻ Actualizar", style="Muted.TButton",
                   command=self.refresh).pack(anchor="e", pady=(8,0))

        right = tk.Frame(body, bg=C["panel"])
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="  Vendedor", bg=C["panel"], fg=C["text"], font=FONT_HEAD, pady=12).pack(anchor="w")

        form = tk.Frame(right, bg=C["panel"])
        form.pack(fill="x", padx=16, pady=4)
        form.columnconfigure(0, weight=1)

        self.f_nombre   = LabeledEntry(form, "Nombre completo"); self.f_nombre.configure(bg=C["panel"])
        self.f_nombre.grid(row=0, column=0, sticky="ew", pady=5)
        self.f_email    = LabeledEntry(form, "Email"); self.f_email.configure(bg=C["panel"])
        self.f_email.grid(row=1, column=0, sticky="ew", pady=5)
        self.f_telefono = LabeledEntry(form, "Teléfono"); self.f_telefono.configure(bg=C["panel"])
        self.f_telefono.grid(row=2, column=0, sticky="ew", pady=5)
        self.f_codigo   = LabeledEntry(form, "Código vendedor"); self.f_codigo.configure(bg=C["panel"])
        self.f_codigo.grid(row=3, column=0, sticky="ew", pady=5)
        self.f_comision = LabeledEntry(form, "Comisión (%)"); self.f_comision.configure(bg=C["panel"])
        self.f_comision.set("0.00")
        self.f_comision.grid(row=4, column=0, sticky="ew", pady=5)
        self.f_password = LabeledEntry(form, "Contraseña (opcional)", show="*")
        self.f_password.configure(bg=C["panel"])
        self.f_password.grid(row=5, column=0, sticky="ew", pady=5)

        ttk.Separator(right).pack(fill="x", padx=10, pady=8)
        btn_f = tk.Frame(right, bg=C["panel"]); btn_f.pack(fill="x", padx=16, pady=(0,10))
        ttk.Button(btn_f, text="💾 Guardar nuevo", style="Accent.TButton", command=self._save).pack(fill="x", pady=3)
        ttk.Button(btn_f, text="✖ Limpiar",        style="Muted.TButton",  command=self._clear).pack(fill="x")

    def refresh(self):
        vendedores = VendedorController.listar()
        self.tree.tree.delete(*self.tree.tree.get_children())
        for i, v in enumerate(vendedores):
            tag = "odd" if i%2 else "even"
            self.tree.tree.insert("", "end", iid=v.id, tags=(tag,),
                values=(v.nombre, v.email, v.codigo, f"{v.comision:.1f}%"))
        self._vendedores = vendedores

    def _on_select(self, _=None):
        iid = self.tree.selected_iid()
        if not iid: return
        v = next((x for x in self._vendedores if x.id == iid), None)
        if not v: return
        self._sel = v
        self.f_nombre.set(v.nombre); self.f_email.set(v.email)
        self.f_codigo.set(v.codigo); self.f_comision.set(str(v.comision))

    def _clear(self):
        self._sel = None
        for f in [self.f_nombre, self.f_email, self.f_telefono, self.f_codigo]:
            f.clear()
        self.f_comision.set("0.00")
        self.f_password.clear()

    def _delete_selected(self):
        iid = self.tree.selected_iid()
        if not iid:
            messagebox.showwarning("Selecciona", "Selecciona un vendedor para eliminar.")
            return
        v = next((x for x in self._vendedores if x.id == iid), None)
        if not v:
            messagebox.showerror("Error", "Vendedor no encontrado.")
            return
        if not messagebox.askyesno("Confirmar", f"Eliminar a {v.nombre}? Esta acción desactivará su rol."):
            return
        ok, msg = VendedorController.eliminar(v.id)
        if ok:
            messagebox.showinfo("✔", msg)
            self.refresh()
            # si la vista de nueva venta está abierta, refrescar combos
            try:
                app = self.winfo_toplevel()
                nv = app._views.get('nueva_venta') if hasattr(app, '_views') else None
                if nv and hasattr(nv, '_load_combos'):
                    nv._load_combos()
            except Exception:
                pass
        else:
            messagebox.showerror("Error", msg)

    def _save(self):
        # Generar contraseña temporal si no se proporcionó
        provided_pw = self.f_password.get().strip()
        gen_pw = None
        if not provided_pw:
            from uuid import uuid4
            gen_pw = uuid4().hex[:8]
        pw_to_save = provided_pw or gen_pw or ''

        data = {'nombre': self.f_nombre.get(), 'email': self.f_email.get(),
                'telefono': self.f_telefono.get(), 'codigo': self.f_codigo.get(),
                'comision': self.f_comision.get(), 'password': pw_to_save,
                'persona_id': self._sel.persona_id if self._sel else None,
                'rol_id':     self._sel.id if self._sel else None}
        ok, msg = VendedorController.guardar(data)
        if ok:
            # Mostrar contraseña generada si aplica
            if gen_pw:
                messagebox.showinfo("✔ Vendedor guardado", f"{msg}\nContraseña temporal: {gen_pw}")
            else:
                messagebox.showinfo("✔", msg)
        else:
            messagebox.showerror("Error", msg)
        if ok:
            self._clear(); self.refresh()
            # Actualizar vista de nueva venta si está abierta
            try:
                app = self.winfo_toplevel()
                nv = app._views.get('nueva_venta') if hasattr(app, '_views') else None
                if nv and hasattr(nv, '_load_combos'):
                    nv._load_combos()
            except Exception:
                pass
