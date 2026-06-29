import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from views.theme import C, FONT_HEAD, FONT_SMALL, apply_theme, sidebar_btn, active_sidebar_btn


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Ventas")
        
        # Ajustar tamaño inicial relativo a la pantalla
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = int(sw * 0.9), int(sh * 0.85)
        self.geometry(f"{w}x{h}")
        self.minsize(900, 600)
        self.configure(bg=C["bg"])
        apply_theme(self)
        
        self._views = {}
        self._current = None
        self._sidebar_btns = {}
        
        # Rol por defecto inicial (se actualizará en set_logged_user)
        self.role = 'Dueño'
        self.current_user = None
        
        # Construimos el cascarón de la interfaz (Sidebar fija y panel de contenido)
        self._build()

    def _build(self):
        # ── Root layout ──────────────────────────────────────
        root_frame = tk.Frame(self, bg=C["bg"])
        root_frame.pack(fill="both", expand=True)
        root_frame.columnconfigure(1, weight=1)
        root_frame.rowconfigure(0, weight=1)

        # ── SIDEBAR ──────────────────────────────────────────
        sidebar = tk.Frame(root_frame, bg=C["panel"], width=220)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo / título
        logo_f = tk.Frame(sidebar, bg=C["panel"])
        logo_f.pack(fill="x", pady=(20, 8))
        tk.Label(logo_f, text="🛍  VentasPro", bg=C["panel"],
                 fg=C["accent"], font=("Segoe UI", 15, "bold"),
                 padx=16).pack(anchor="w")
        tk.Label(logo_f, text="Sistema de ventas local", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL, padx=16).pack(anchor="w")

        # Selector de rol (Dueño / Vendedor)
        role_f = tk.Frame(sidebar, bg=C["panel"])
        role_f.pack(fill="x", pady=(8, 10), padx=12)
        tk.Label(role_f, text="Rol:", bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(side="left")
        
        self._role_combo = ttk.Combobox(role_f, values=["Dueño", "Vendedor"], state="disabled", width=18)
        self._role_combo.set("— Iniciar sesión —")
        self._role_combo.pack(side="left", padx=(8,0))

        ttk.Separator(sidebar).pack(fill="x", padx=12, pady=8)

        # Contenedor dinámico para botones de navegación (se poblará en set_logged_user)
        self._nav_frame = tk.Frame(sidebar, bg=C["panel"])
        self._nav_frame.pack(fill="both", expand=True, padx=4, pady=(6,0))

        # Logout button + footer sidebar
        self._logout_btn = ttk.Button(sidebar, text="Cerrar sesión", command=self.logout, style="Muted.TButton")
        self._logout_btn.pack(fill="x", padx=12, pady=(0,6), side="bottom")
        ttk.Separator(sidebar).pack(fill="x", padx=12, pady=4, side="bottom")
        tk.Label(sidebar, text="SQLite • MVC • Python 3",
             bg=C["panel"], fg=C["muted"], font=FONT_SMALL, pady=8).pack(side="bottom")

        # ── CONTENIDO PRINCIPAL ──────────────────────────────
        self._content = tk.Frame(root_frame, bg=C["bg"])
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.rowconfigure(0, weight=1)
        self._content.columnconfigure(0, weight=1)

    def set_logged_user(self, persona, rol):
        """
        Este método es invocado por el AppController inmediatamente 
        después de un login exitoso. Reconstruye el menú basado en el rol real.
        """
        self.current_user = persona
        self.role = rol.tipo if rol else 'Dueño'
        
        try:
            self._role_combo.config(state='normal')
            self._role_combo.set(self.role)
            self._role_combo.config(state='disabled')
        except Exception:
            pass
            
        # Limpiar vistas previas si existieran
        for k, v in list(self._views.items()):
            try:
                v.destroy()
            except Exception:
                pass
        self._views.clear()
        self._current = None
        
        # Construir los botones del menú de navegación según los permisos del rol
        self._build_nav()
        
        # Redirigir automáticamente a la pantalla de inicio del sistema
        self._navigate('dashboard')

    def _navigate(self, key: str):
        if self._current == key:
            return
            
        # Actualizar estilos visuales de los botones de la barra lateral
        for k, btn in self._sidebar_btns.items():
            is_active = k == key
            bg = C["accent"] if is_active else C["panel"]
            fg_label = C["bg"] if is_active else C["muted"]
            font_w = "bold" if is_active else "normal"
            btn.config(bg=bg)
            for w in btn.winfo_children():
                if isinstance(w, tk.Label):
                    w.config(bg=bg, fg=fg_label, font=("Segoe UI", 11, font_w))

        # Ocultar la vista que estaba activa
        if self._current and self._current in self._views:
            self._views[self._current].grid_remove()

        # Crear o recuperar la vista solicitada
        if key not in self._views:
            try:
                view = self._create_view(key)
                self._views[key] = view
                view.grid(row=0, column=0, sticky="nsew", in_=self._content)
                if hasattr(view, 'refresh'):
                    try:
                        view.refresh()
                    except Exception:
                        print('Error durante view.refresh():', traceback.format_exc())
            except Exception:
                tb = traceback.format_exc()
                print(tb)
                try:
                    import os
                    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'error.log')
                    with open(log_path, 'a', encoding='utf-8') as lf:
                        lf.write(f'--- Error al crear vista {key} ---\n')
                        lf.write(tb + '\n')
                except Exception:
                    pass
                messagebox.showerror('Error', f'Ocurrió un error al crear la vista "{key}". Revisa error.log.')
                return
        else:
            view = self._views[key]
            if hasattr(view, 'refresh'):
                view.refresh()
            view.grid(row=0, column=0, sticky="nsew", in_=self._content)

        self._current = key

    def logout(self):
        """ Destruye la sesión actual y solicita al controlador reabrir el login """
        # 1. Limpiar datos de usuario en memoria
        self.current_user = None
        self.role = 'Dueño'
        
        # 2. Destruir y limpiar todas las vistas cargadas para liberar memoria
        for k, v in list(self._views.items()):
            try:
                v.destroy()
            except Exception:
                pass
        self._views.clear()
        self._current = None
        
        # 3. Limpiar los botones del menú lateral
        for w in self._nav_frame.winfo_children():
            w.destroy()
            
        # 4. Destruir por completo la ventana principal actual
        self.destroy()
        
        # 5. Levantar una nueva instancia del controlador para mostrar el Login limpio
        from controllers.app_controller import AppController
        AppController()

    def _build_nav(self):
        # Limpiar botones existentes en el contenedor de navegación
        for w in self._nav_frame.winfo_children():
            w.destroy()
        self._sidebar_btns.clear()
        
        # Crear botones adaptados dinámicamente según las restricciones de rol
        for key, icon, label in self._nav_items_for_role():
            btn = sidebar_btn(self._nav_frame, label, icon, lambda k=key: self._navigate(k))
            btn.pack(fill="x", padx=8, pady=2)
            self._sidebar_btns[key] = btn

    def _nav_items_for_role(self):
        base = [
            ("dashboard",   "📊", "Dashboard"),
            ("nueva_venta", "🧾", "Nueva Venta"),
            ("historial",   "📋", "Historial"),
            ("clientes",    "👤", "Clientes"),
        ]
        owner_extra = [
            ("productos",   "📦", "Productos"),
            ("stock",       "🏪", "Inventario"),
            ("vendedores",  "👷", "Vendedores"),
        ]
        if self.role == 'Dueño':
            return base + owner_extra
        return base

    def _create_view(self, key: str) -> tk.Frame:
        from views.dashboard_view  import DashboardView
        from views.venta_view      import NuevaVentaView
        from views.historial_view  import HistorialView
        from views.productos_view  import ProductosView
        from views.stock_view      import StockView
        from views.personas_view   import ClientesView, VendedoresView

        mapping = {
            "dashboard":   DashboardView,
            "nueva_venta": NuevaVentaView,
            "historial":   HistorialView,
            "productos":   ProductosView,
            "stock":       StockView,
            "clientes":    ClientesView,
            "vendedores":  VendedoresView,
        }
        
        cls = mapping[key]
        view = cls(self._content)
        view.grid(row=0, column=0, sticky="nsew")
        return view