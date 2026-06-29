import tkinter as tk
from views.login_view import LoginView  
from views.main_window import MainWindow
from views.theme import C

class AppController:
    def __init__(self):
        # 1. Instanciamos tu MainWindow original (creará el tk.Tk interno)
        self.main_app = MainWindow()
        
        # 2. La ocultamos inmediatamente antes de que el usuario note que se abrió
        self.main_app.withdraw()
        
        # 3. Lanzamos de inmediato la ventana flotante de Login
        self.open_login()
        
        # 4. Iniciamos el ciclo de vida usando la app principal
        self.main_app.mainloop()

    def open_login(self):
        # El padre del Toplevel será nuestra ventana principal oculta
        self.login_window = tk.Toplevel(self.main_app)
        self.login_window.title("VentasPro - Iniciar Sesión")
        self.login_window.configure(bg=C["bg"])
        self.login_window.geometry("450x400")
        self.login_window.resizable(False, False)
        
        # Si el usuario cierra el login en la 'X', destruimos todo el proceso
        self.login_window.protocol("WM_DELETE_WINDOW", self.main_app.destroy)
        
        # Insertamos tu LoginView pasándole la ventana flotante como contenedor
        self.login_frame = LoginView(self.login_window, on_login=self.handle_login_success)
        self.login_frame.pack(fill="both", expand=True)

    def handle_login_success(self, persona, rol):
        # 1. Eliminamos la ventana de login
        self.login_window.destroy()
        
        # 2. Inyectamos de forma segura los datos de sesión directo en tu main_app existente
        # usando el método nativo que tú ya programaste
        self.main_app.set_logged_user(persona, rol)
        
        # 3. Hacemos visible la ventana principal con todo su contenido construido de fábrica
        self.main_app.deiconify()