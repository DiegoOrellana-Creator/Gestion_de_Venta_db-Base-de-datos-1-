import tkinter as tk
from tkinter import ttk, messagebox
from views.theme import C, FONT_HEAD, LabeledEntry
from controllers.controllers import AuthController


class LoginView(tk.Frame):
    def __init__(self, parent, on_login):
        super().__init__(parent, bg=C["bg"])
        self.on_login = on_login
        self._build()

    def _build(self):
        box = tk.Frame(self, bg=C["bg"])
        box.place(relx=0.5, rely=0.4, anchor="c")

        tk.Label(box, text="Iniciar sesión", bg=C["bg"], fg=C["text"], font=FONT_HEAD).pack()
        tk.Label(box, text="Ingresa el correo y la contraseña", bg=C["bg"], fg=C["muted"]).pack(pady=(4,12))

        form = tk.Frame(box, bg=C["bg"]) ; form.pack()
        self.f_email = LabeledEntry(form, "Email")
        self.f_email.pack()
        self.f_password = LabeledEntry(form, "Contraseña", show="*")
        self.f_password.pack()

        btn_f = tk.Frame(box, bg=C["bg"]) ; btn_f.pack(pady=(12,0))
        ttk.Button(btn_f, text="Iniciar sesión", command=self._login).pack()

    def _login(self):
        email = self.f_email.get().strip()
        password = self.f_password.get().strip()
        if not email:
            messagebox.showerror("Error", "Ingrese un email válido.")
            return
        ok, msg, persona, rol = AuthController.authenticate(email, password)
        if not ok:
            messagebox.showerror("Error", msg)
            return
        messagebox.showinfo("Bienvenido", f"Hola {persona.nombre} — rol: {rol.tipo}")
        if callable(self.on_login):
            self.on_login(persona, rol)
    
    def refresh(self):
        # limpiar campos y enfocar email
        try:
            self.f_email.clear()
            self.f_password.clear()
            self.f_email.entry.focus_set()
        except Exception:
            pass