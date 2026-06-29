import sqlite3
import os
from uuid import uuid4

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ventas.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def initialize_db():
    conn = get_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
        
    # Añadir columna password en personas si no existe (Migración)
    cols = [r['name'] for r in conn.execute("PRAGMA table_info(personas)").fetchall()]
    if 'password' not in cols:
        try:
            conn.execute("ALTER TABLE personas ADD COLUMN password TEXT")
            conn.execute("UPDATE personas SET password=? WHERE email=?", ('12975795', 'diego@tienda'))
            conn.execute("UPDATE personas SET password=? WHERE email=?", ('maria123', 'maria@tienda.com'))
            conn.execute("UPDATE personas SET password=? WHERE email=?", ('jorge123', 'jorge@tienda.com'))
        except Exception:
            pass

    # Añadir columna descuento en productos si no existe (Migración)
    cols = [r['name'] for r in conn.execute("PRAGMA table_info(productos)").fetchall()]
    if 'descuento' not in cols:
        try:
            conn.execute("ALTER TABLE productos ADD COLUMN descuento REAL NOT NULL DEFAULT 0.0")
        except Exception:
            pass
            
    try:
        conn.execute("""
            UPDATE personas 
            SET nombre = 'Diego Orellana Gutierrez' 
            WHERE id IN (SELECT persona_id FROM roles WHERE tipo = 'Dueño')
        """)
    except Exception:
        pass
        
    conn.commit()
    _seed_demo_data(conn)
    conn.close()


def _seed_demo_data(conn: sqlite3.Connection):
    if conn.execute("SELECT COUNT(*) FROM personas").fetchone()[0] > 0:
        return

    tipos = [
        (str(uuid4()), 'Deportivo'),
        (str(uuid4()), 'Casual'),
        (str(uuid4()), 'Formal'),
        (str(uuid4()), 'Bota'),
    ]
    conn.executemany("INSERT INTO tipo_calzado VALUES (?,?)", tipos)

    tienda_id  = str(uuid4())
    almacen_id = str(uuid4())
    conn.execute("INSERT INTO tiendas   VALUES (?,?,?,?)", (tienda_id,  'Tienda Central', 'Av. Siempre Viva 123', 200))
    conn.execute("INSERT INTO almacenes VALUES (?,?,?,?)", (almacen_id, 'Almacén Norte',  'Calle Industrial 45',  500))

    def _persona(nombre, email, tel, sexo, password=""):
        pid = str(uuid4())
        conn.execute("INSERT INTO personas(id,nombre,email,password,telefono,sexo) VALUES (?,?,?,?,?,?)",
                     (pid, nombre, email, password, tel, sexo))
        return pid

    def _rol(persona_id, tipo):
        rid = str(uuid4())
        conn.execute("INSERT INTO roles(id,persona_id,tipo) VALUES (?,?,?)", (rid, persona_id, tipo))
        return rid

    # Cambiado permanentemente a tu nombre aquí
    dp = _persona('Diego Orellana Gutierrez', 'diego@tienda', '591-77000001', 'M', '12975795')
    dr = _rol(dp, 'Dueño')
    conn.execute("INSERT INTO duenos VALUES (?)", (dr,))

    # Vendedores de demo
    vp1 = _persona('María López', 'maria@tienda.com', '591-77000002', 'F', 'maria123')
    vr1 = _rol(vp1, 'Vendedor')
    conn.execute("INSERT INTO vendedores VALUES (?,?,?)", (vr1, 'VEN-001', 5.00))

    vp2 = _persona('Jorge Quispe', 'jorge@tienda.com', '591-77000003', 'M', 'jorge123')
    vr2 = _rol(vp2, 'Vendedor')
    conn.execute("INSERT INTO vendedores VALUES (?,?,?)", (vr2, 'VEN-002', 4.50))

    # Clientes de demo
    clientes_ids = []
    for i, (nom, email, tel, sx) in enumerate([
        ('Carlos Mendoza', 'carlos@gmail.com', '591-70011111', 'M'),
        ('Ana García',     'ana@gmail.com',    '591-70022222', 'F'),
        ('Luis Rojas',     'luis@gmail.com',   '591-70033333', 'M'),
        ('Sara Flores',    'sara@gmail.com',   '591-70044444', 'F'),
    ]):
        cp = _persona(nom, email, tel, sx, f'cliente{i+1}23')
        cr = _rol(cp, 'Cliente')
        conn.execute("INSERT INTO clientes VALUES (?,?,?)", (cr, 0, 0.00))
        clientes_ids.append(cr)

    # Inserciones complementarias de productos y stock
    tipo_dep = tipos[0][0]
    tipo_cas = tipos[1][0]

    def _prod(nombre, precio, marca, tipo):
        pid = str(uuid4())
        conn.execute("INSERT INTO productos(id_producto,nombre,precio,marca,tipo_producto) VALUES (?,?,?,?,?)",
                     (pid, nombre, precio, marca, tipo))
        return pid

    m1 = _prod('Mochila Urbana 25L', 89.99, 'TrailX', 'Mochila')
    conn.execute("INSERT INTO mochilas VALUES (?,?,?,?)", (m1, 'Poliéster 600D', 3, 'Negro'))

    m2 = _prod('Mochila Escolar Classic', 55.00, 'EduPack', 'Mochila')
    conn.execute("INSERT INTO mochilas VALUES (?,?,?,?)", (m2, 'Nylon', 2, 'Azul'))

    c1 = _prod('Zapatilla Running Air', 120.00, 'SpeedFit', 'Calzado')
    conn.execute("INSERT INTO calzados VALUES (?,?,?,?,?,?)", (c1, 42.0, 'Mesh', 'Unisex', 'Blanco', tipo_dep))

    c2 = _prod('Bota Casual Cuero', 199.99, 'UrbanStep', 'Calzado')
    conn.execute("INSERT INTO calzados VALUES (?,?,?,?,?,?)", (c2, 40.0, 'Cuero', 'M', 'Marrón', tipo_cas))

    p1 = _prod('Pelota Fútbol N°5', 45.00, 'GoalPro', 'Pelota')
    conn.execute("INSERT INTO pelotas VALUES (?,?,?,?)", (p1, 'Fútbol', 5, 1))

    for pid, qty in [(m1, 20), (m2, 35), (c1, 15), (c2, 8), (p1, 40)]:
        conn.execute("INSERT INTO stock_ubicacion(id,tienda_id,producto_id,cantidad) VALUES (?,?,?,?)",
                     (str(uuid4()), tienda_id, pid, qty))

    conn.commit()