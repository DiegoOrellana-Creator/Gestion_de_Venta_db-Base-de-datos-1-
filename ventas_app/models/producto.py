from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4
from database.db import get_connection


@dataclass
class Producto:
    id_producto: str = field(default_factory=lambda: str(uuid4()))
    nombre: str = ""
    precio: float = 0.0
    descuento: float = 0.0
    activo: int = 1
    fecha_registro: str = ""
    marca: str = ""
    tipo_producto: str = "Mochila"
    stock_total: int = 0

    @staticmethod
    def get_all(solo_activos=True):
        conn = get_connection()
        filtro = "WHERE p.activo=1" if solo_activos else ""
        rows = conn.execute(f"""
            SELECT p.id_producto, p.nombre, p.precio, p.descuento, p.activo,
                   p.fecha_registro, p.marca, p.tipo_producto,
                   COALESCE(SUM(s.cantidad),0) AS stock_total
            FROM productos p
            LEFT JOIN stock_ubicacion s ON s.producto_id = p.id_producto
            {filtro}
            GROUP BY p.id_producto
            ORDER BY p.nombre
        """).fetchall()
        conn.close()
        return [Producto(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(pid: str):
        conn = get_connection()
        r = conn.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.descuento, p.activo,
                   p.fecha_registro, p.marca, p.tipo_producto,
                   COALESCE(SUM(s.cantidad),0) AS stock_total
            FROM productos p
            LEFT JOIN stock_ubicacion s ON s.producto_id = p.id_producto
            WHERE p.id_producto=?
            GROUP BY p.id_producto
        """, (pid,)).fetchone()
        conn.close()
        return Producto(**dict(r)) if r else None

    @staticmethod
    def search(term: str):
        conn = get_connection()
        rows = conn.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.descuento, p.activo,
                   p.fecha_registro, p.marca, p.tipo_producto,
                   COALESCE(SUM(s.cantidad),0) AS stock_total
            FROM productos p
            LEFT JOIN stock_ubicacion s ON s.producto_id = p.id_producto
            WHERE p.activo=1 AND (p.nombre LIKE ? OR p.marca LIKE ?)
            GROUP BY p.id_producto
            ORDER BY p.nombre
        """, (f"%{term}%", f"%{term}%")).fetchall()
        conn.close()
        return [Producto(**dict(r)) for r in rows]

    def save(self):
        conn = get_connection()
        conn.execute("""
            INSERT INTO productos(id_producto,nombre,precio,descuento,activo,marca,tipo_producto)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(id_producto) DO UPDATE SET
                nombre=excluded.nombre, precio=excluded.precio,
                descuento=excluded.descuento, activo=excluded.activo,
                marca=excluded.marca, tipo_producto=excluded.tipo_producto
        """, (self.id_producto, self.nombre, self.precio,
              self.descuento, self.activo, self.marca, self.tipo_producto))
        conn.commit(); conn.close()

    def precio_con_descuento(self) -> float:
        descuento = max(0.0, min(self.descuento or 0.0, 100.0))
        if descuento <= 0:
            return round(self.precio, 2)
        return round(self.precio * (1 - descuento / 100), 2)

    def delete(self):
        conn = get_connection()
        conn.execute("UPDATE productos SET activo=0 WHERE id_producto=?", (self.id_producto,))
        conn.commit(); conn.close()

    def descontar_stock(self, cantidad: int):
        conn = get_connection()
        conn.execute("""
            UPDATE stock_ubicacion SET cantidad = cantidad - ?
            WHERE id = (
                SELECT id FROM stock_ubicacion
                WHERE producto_id=? AND cantidad >= ?
                LIMIT 1
            )
        """, (cantidad, self.id_producto, cantidad))
        conn.commit(); conn.close()


@dataclass
class StockUbicacion:
    id: str = field(default_factory=lambda: str(uuid4()))
    tienda_id: Optional[str] = None
    almacen_id: Optional[str] = None
    producto_id: str = ""
    cantidad: int = 0
    fecha_ingreso: str = ""
    producto_nombre: str = ""
    ubicacion_nombre: str = ""

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT s.id, s.tienda_id, s.almacen_id, s.producto_id,
                   s.cantidad, s.fecha_ingreso,
                   p.nombre AS producto_nombre,
                   COALESCE(t.nombre, a.nombre) AS ubicacion_nombre
            FROM stock_ubicacion s
            JOIN productos p ON p.id_producto = s.producto_id
            LEFT JOIN tiendas   t ON t.id = s.tienda_id
            LEFT JOIN almacenes a ON a.id = s.almacen_id
            ORDER BY ubicacion_nombre, p.nombre
        """).fetchall()
        conn.close()
        return [StockUbicacion(**dict(r)) for r in rows]

    def save(self):
        conn = get_connection()
        conn.execute("""
            INSERT INTO stock_ubicacion(id,tienda_id,almacen_id,producto_id,cantidad)
            VALUES (?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET cantidad=excluded.cantidad
        """, (self.id, self.tienda_id, self.almacen_id, self.producto_id, self.cantidad))
        conn.commit(); conn.close()
