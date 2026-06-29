# 🛍 VentasPro — Sistema de Registro de Ventas

Aplicación de escritorio Python con arquitectura **MVC** y base de datos **SQLite local**.

---

## 📁 Estructura del proyecto

```
ventas_app/
├── main.py                      ← Punto de entrada
├── ventas.db                    ← Base de datos SQLite (se crea automáticamente)
│
├── database/
│   ├── db.py                    ← Conexión, inicialización y datos demo
│   └── schema.sql               ← Esquema SQL (adaptado de PostgreSQL)
│
├── models/                      ← M — Modelos (acceso a datos)
│   ├── persona.py               ← Persona, Rol, Cliente, Vendedor
│   ├── producto.py              ← Producto, StockUbicacion
│   └── venta.py                 ← Venta, DetalleVenta
│
├── controllers/                 ← C — Controladores (lógica de negocio)
│   └── controllers.py           ← VentaController, ProductoController,
│                                   ClienteController, VendedorController
│
└── views/                       ← V — Vistas (interfaz Tkinter)
    ├── theme.py                 ← Paleta, estilos y widgets reutilizables
    ├── main_window.py           ← Ventana principal + sidebar
    ├── dashboard_view.py        ← Dashboard con métricas
    ├── venta_view.py            ← POS / Nueva venta
    ├── historial_view.py        ← Historial y anulación de ventas
    ├── productos_view.py        ← CRUD de productos
    ├── stock_view.py            ← Inventario por ubicación
    └── personas_view.py         ← Gestión de clientes y vendedores
```

---

## ⚡ Requisitos

- Python 3.10 o superior
- Tkinter (incluido en Python; en Linux instalar con `sudo apt install python3-tk`)

**Sin dependencias externas** — solo librería estándar de Python.

---

## 🚀 Instalación y ejecución

```bash
# 1. Descomprimir / clonar el proyecto
cd ventas_app

# 2. Ejecutar directamente
python main.py
```

La base de datos `ventas.db` se crea automáticamente en la primera ejecución
con datos demo (clientes, vendedores y productos de ejemplo).

---

## 🗄️ Esquema de base de datos

El esquema es una traducción fiel de PostgreSQL a SQLite:

| PostgreSQL            | SQLite                              |
|-----------------------|-------------------------------------|
| `UUID`                | `TEXT` (generado con `uuid4()`)     |
| `NUMERIC(10,2)`       | `REAL`                              |
| `TIMESTAMP WITH TZ`   | `TEXT` ISO-8601                     |
| `BOOLEAN`             | `INTEGER` (1=TRUE, 0=FALSE)         |
| `gen_random_uuid()`   | Generado en Python antes de INSERT  |
| `ON CONFLICT` (UPSERT)| Soportado en SQLite ≥ 3.24          |

### Tablas principales
- **personas** → padre de todos los actores
- **roles** → tabla intermedia (`Dueño`, `Vendedor`, `Cliente`)
- **clientes / vendedores / duenos** → especializaciones de rol
- **productos** → padre con subtipos `mochilas`, `calzados`, `pelotas`
- **tipo_calzado** → catálogo auxiliar
- **tiendas / almacenes** → ubicaciones
- **stock_ubicacion** → inventario por ubicación
- **ventas / detalle_ventas** → cabecera y cuerpo de ventas

---

## 🎨 Funcionalidades

| Módulo         | Funciones                                           |
|----------------|-----------------------------------------------------|
| Dashboard      | Métricas totales, últimas ventas, top productos     |
| Nueva Venta    | POS con búsqueda, carrito, validación de stock      |
| Historial      | Listado, filtro, detalle y anulación de ventas      |
| Productos      | CRUD de productos (Mochila / Calzado / Pelota)      |
| Inventario     | Stock por tienda/almacén, alertas de stock bajo     |
| Clientes       | Alta y consulta de clientes con puntos              |
| Vendedores     | Alta y consulta del equipo de ventas                |

---

## 🏗️ Patrón MVC aplicado

```
Vista (Tkinter)
   │  eventos/acciones
   ▼
Controlador (controllers.py)
   │  lógica de negocio + validaciones
   ▼
Modelo (models/*.py)
   │  queries SQL
   ▼
Base de datos (ventas.db — SQLite)
```
