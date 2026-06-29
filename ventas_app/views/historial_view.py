import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import C, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_MONO, ScrolledTree
from controllers.controllers import VentaController


class HistorialView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._build()
        self.refresh()

    def _build(self):
        ttk.Label(self, text="Historial de Ventas", style="Title.TLabel").pack(anchor="w", padx=28, pady=(24,4))
        ttk.Label(self, text="Consulta y gestiona todas las transacciones", style="Muted.TLabel").pack(anchor="w", padx=28)
        ttk.Separator(self).pack(fill="x", padx=28, pady=12)

        # Toolbar
        toolbar = tk.Frame(self, bg=C["bg"])
        toolbar.pack(fill="x", padx=28, pady=(0, 8))
        self.var_filtro = tk.StringVar()
        self.var_filtro.trace_add("write", lambda *_: self._filter())
        self.var_fecha_reporte = tk.StringVar(value=datetime.date.today().isoformat())
        ttk.Label(toolbar, text="Buscar:", style="Muted.TLabel").pack(side="left", padx=(0,6))
        ttk.Entry(toolbar, textvariable=self.var_filtro, width=30).pack(side="left")
        ttk.Label(toolbar, text="Fecha (YYYY-MM-DD):", style="Muted.TLabel").pack(side="left", padx=(10,6))
        ttk.Entry(toolbar, textvariable=self.var_fecha_reporte, width=12).pack(side="left")
        ttk.Button(toolbar, text="↻  Actualizar", style="Muted.TButton",
                   command=self.refresh).pack(side="right")
        ttk.Button(toolbar, text="📄  Generar reporte", style="Muted.TButton",
                   command=self._export_report).pack(side="right", padx=6)
        ttk.Button(toolbar, text="📅  Reporte por día", style="Muted.TButton",
                   command=self._export_daily_report).pack(side="right", padx=6)
        ttk.Button(toolbar, text="✕  Anular selección", style="Danger.TButton",
                   command=self._anular).pack(side="right", padx=6)

        # Tabla
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=28, pady=(0,8))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)

        left = tk.Frame(body, bg=C["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        self.tree = ScrolledTree(left, columns=("id_corto","fecha","cliente","vendedor","total","metodo","estado"))
        self.tree.set_columns([
            {"text": "#",        "width": 70},
            {"text": "Fecha",    "width": 135},
            {"text": "Cliente",  "width": 150},
            {"text": "Vendedor", "width": 130},
            {"text": "Total",    "width": 90,  "anchor":"e"},
            {"text": "Método",   "width": 80},
            {"text": "Estado",   "width": 90},
        ])
        self.tree.pack(fill="both", expand=True)
        self.tree.bind_select(self._on_select)

        # Detalle panel
        right = tk.Frame(body, bg=C["panel"])
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="  Detalle", bg=C["panel"], fg=C["text"],
                 font=FONT_HEAD, pady=12).pack(anchor="w")
        self.tree_detalle = ScrolledTree(right, columns=("prod","qty","precio","sub"))
        self.tree_detalle.set_columns([
            {"text": "Producto", "width": 160},
            {"text": "Qty",      "width": 40, "anchor":"center"},
            {"text": "Precio",   "width": 70, "anchor":"e"},
            {"text": "Subtotal", "width": 80, "anchor":"e"},
        ])
        self.tree_detalle.pack(fill="both", expand=True, padx=8, pady=(0,8))

        self.lbl_info = tk.Label(right, text="", bg=C["panel"], fg=C["muted"],
                                  font=FONT_SMALL, wraplength=220, justify="left")
        self.lbl_info.pack(anchor="w", padx=10, pady=6)

    def refresh(self):
        self._all_ventas = VentaController.listar_ventas()
        self._render(self._all_ventas)

    def _render(self, ventas):
        rows = []
        for v in ventas:
            fecha = v.fecha[:16] if v.fecha else ""
            rows.append((str(v.id_venta)[:8]+"…", fecha,
                         v.cliente_nombre, v.vendedor_nombre,
                         f"Bs. {v.total:,.2f}", v.metodo_pago, v.estado))
        # Store full ids as iids
        self.tree.tree.delete(*self.tree.tree.get_children())
        for i, (v, row) in enumerate(zip(ventas, rows)):
            tag = "odd" if i % 2 else "even"
            if v.estado == "Anulada":
                tag = "anulada"
                self.tree.tree.tag_configure("anulada", foreground=C["danger"],
                                              background=C["row_even"])
            self.tree.tree.insert("", "end", iid=v.id_venta, values=row, tags=(tag,))
        self._ventas_shown = ventas

    def _filter(self):
        term = self.var_filtro.get().lower()
        if not term:
            self._render(self._all_ventas)
            return
        filtered = [v for v in self._all_ventas if
                    term in v.cliente_nombre.lower() or
                    term in v.vendedor_nombre.lower() or
                    term in v.metodo_pago.lower() or
                    term in v.estado.lower() or
                    term in (v.fecha or "")]
        self._render(filtered)

    def _on_select(self, _event=None):
        iid = self.tree.selected_iid()
        if not iid: return
        venta = VentaController.obtener_venta(iid)
        if not venta: return
        rows = [(d.producto_nombre, d.cantidad,
                 f"Bs. {d.precio_unitario:.2f}",
                 f"Bs. {d.subtotal:.2f}") for d in venta.detalles]
        self.tree_detalle.load(rows)
        self.lbl_info.config(text=(
            f"Cliente: {venta.cliente_nombre}\n"
            f"Vendedor: {venta.vendedor_nombre}\n"
            f"Fecha: {venta.fecha[:16] if venta.fecha else ''}\n"
            f"Método: {venta.metodo_pago}\n"
            f"Estado: {venta.estado}\n"
            f"Total: Bs. {venta.total:,.2f}"
        ))

    def _export_report(self):
        iid = self.tree.selected_iid()
        if not iid:
            messagebox.showwarning("Selección", "Selecciona una venta para generar el reporte.")
            return
        venta = VentaController.obtener_venta(iid)
        if not venta:
            messagebox.showerror("Error", "No se encontró la venta seleccionada.")
            return

        filename = f"reporte_venta_{iid[:8]}.txt"
        path = filedialog.asksaveasfilename(
            title="Guardar reporte de venta",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            initialfile=filename
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("REPORTE DE VENTA\n")
                f.write("====================\n")
                f.write(f"ID de venta: {venta.id_venta}\n")
                f.write(f"Fecha: {venta.fecha or 'N/A'}\n")
                f.write(f"Cliente: {venta.cliente_nombre}\n")
                f.write(f"Vendedor: {venta.vendedor_nombre}\n")
                f.write(f"Método de pago: {venta.metodo_pago}\n")
                f.write(f"Estado: {venta.estado}\n")
                f.write(f"Total: Bs. {venta.total:,.2f}\n")
                f.write("\nDETALLE DE PRODUCTOS\n")
                f.write("--------------------\n")
                for d in venta.detalles:
                    f.write(f"{d.producto_nombre} | Qty: {d.cantidad} | Precio: Bs. {d.precio_unitario:,.2f} | Subtotal: Bs. {d.subtotal:,.2f}\n")
            messagebox.showinfo("Reporte guardado", f"Reporte guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el reporte:\n{e}")

    def _export_daily_report(self):
        fecha = self.var_fecha_reporte.get().strip()
        if not fecha:
            messagebox.showwarning("Fecha inválida", "Ingresa una fecha en formato YYYY-MM-DD.")
            return
        try:
            datetime.datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Fecha inválida", "El formato debe ser YYYY-MM-DD.")
            return

        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reportes por dia")
        os.makedirs(reports_dir, exist_ok=True)
        path = os.path.join(reports_dir, f"reporte_ventas_{fecha}.pdf")

        ok, msg = VentaController.generar_reporte_dia(fecha, path)
        if ok:
            messagebox.showinfo("Reporte guardado", msg)
        else:
            messagebox.showerror("Error", msg)

    def _anular(self):
        iid = self.tree.selected_iid()
        if not iid:
            messagebox.showwarning("Selección", "Selecciona una venta.")
            return
        if not messagebox.askyesno("Anular venta",
                                    "¿Seguro que deseas anular esta venta?\nSe revertirá el stock."):
            return
        ok, msg = VentaController.anular_venta(iid)
        if ok:
            messagebox.showinfo("✔ Anulada", msg)
            self.refresh()
        else:
            messagebox.showerror("Error", msg)
