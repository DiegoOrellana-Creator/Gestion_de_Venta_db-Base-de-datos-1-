import tkinter as tk
from datetime import date
from tkinter import ttk
from views.theme import C, FONT_TITLE, FONT_HEAD, FONT_BODY, FONT_SMALL, StatCard, ScrolledTree
from controllers.controllers import VentaController


class DashboardView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self._build()
        self.refresh()

    def _build(self):
        # Título y usuario
        top_row = tk.Frame(self, bg=C["bg"]) ; top_row.pack(fill="x", padx=28, pady=(24,4))
        ttk.Label(top_row, text="Dashboard", style="Title.TLabel").pack(side="left")
        self.lbl_user = ttk.Label(top_row, text="Usuario: —", style="Muted.TLabel")
        self.lbl_user.pack(side="right")
        ttk.Label(self, text="Resumen general de ventas", style="Muted.TLabel").pack(anchor="w", padx=28)
        ttk.Separator(self).pack(fill="x", padx=28, pady=12)

        # Fila de stats
        self.cards_frame = tk.Frame(self, bg=C["bg"])
        self.cards_frame.pack(fill="x", padx=28, pady=(0, 18))
        for i in range(4):
            self.cards_frame.columnconfigure(i, weight=1)

        self.card_ventas    = StatCard(self.cards_frame, "Total Ventas",    "—",         C["accent"])
        self.card_ingresos  = StatCard(self.cards_frame, "Ingresos Bs.",    "—",         C["accent2"])
        self.card_ticket    = StatCard(self.cards_frame, "Ticket Promedio", "—",         C["warning"])
        self.card_anuladas  = StatCard(self.cards_frame, "Anuladas",        "—",         C["danger"])
        for i, c in enumerate([self.card_ventas, self.card_ingresos, self.card_ticket, self.card_anuladas]):
            c.grid(row=0, column=i, sticky="nsew", padx=6, pady=4, ipadx=4)

        # Sección inferior
        bottom = tk.Frame(self, bg=C["bg"])
        bottom.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=1)

        # Últimas ventas
        left = tk.Frame(bottom, bg=C["panel"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(left, text="  Últimas ventas", bg=C["panel"], fg=C["text"],
                 font=FONT_HEAD, pady=12).pack(anchor="w")
        self.tree_ventas = ScrolledTree(left, columns=("fecha","cliente","total","estado","metodo"))
        self.tree_ventas.set_columns([
            {"text": "Fecha",    "width": 140},
            {"text": "Cliente",  "width": 160},
            {"text": "Total Bs.","width": 90, "anchor": "e"},
            {"text": "Estado",   "width": 90},
            {"text": "Método",   "width": 80},
        ])
        self.tree_ventas.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Top productos
        right = tk.Frame(bottom, bg=C["panel"])
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="  Top productos vendidos", bg=C["panel"],
                 fg=C["text"], font=FONT_HEAD, pady=12).pack(anchor="w")
        self.tree_top = ScrolledTree(right, columns=("producto", "qty"))
        self.tree_top.set_columns([
            {"text": "Producto", "width": 180},
            {"text": "Cantidad", "width": 70, "anchor": "e"},
        ])
        self.tree_top.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Refresh button
        ttk.Button(self, text="↻  Actualizar", style="Muted.TButton",
                   command=self.refresh).pack(anchor="e", padx=28, pady=(0, 8))

    def refresh(self):
        today = date.today().isoformat()
        stats, top = VentaController.dashboard(today)
        # Mostrar nombre del usuario si está logueado
        user = getattr(self.winfo_toplevel(), 'current_user', None)
        if user:
            self.lbl_user.config(text=f"Usuario: {user.nombre}")
        else:
            self.lbl_user.config(text="Usuario: —")
        self.card_ventas.winfo_children()[1].config(text=str(stats["total_ventas"]))
        self.card_ingresos.winfo_children()[1].config(text=f"Bs. {stats['ingresos_totales']:,.2f}")
        self.card_ticket.winfo_children()[1].config(text=f"Bs. {stats['ticket_promedio']:,.2f}")
        self.card_anuladas.winfo_children()[1].config(text=str(stats["anuladas"]))

        ventas = VentaController.obtener_ventas_por_dia(today)
        rows = []
        for v in ventas[:15]:
            fecha = v.fecha[:16] if v.fecha else ""
            color = C["danger"] if v.estado == "Anulada" else C["accent"]
            rows.append((fecha, v.cliente_nombre, f"Bs. {v.total:,.2f}", v.estado, v.metodo_pago))
        self.tree_ventas.load(rows)

        self.tree_top.load([(t["nombre"], t["qty"]) for t in top])
