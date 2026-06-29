import sys
import os

# Asegura que los imports funcionen desde cualquier directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import initialize_db
from controllers.app_controller import AppController


def main():
    # 1. Inicializar BD y datos demo
    initialize_db()

    # 2. Lanzar el controlador del flujo de la app
    AppController()


if __name__ == "__main__":
    main()