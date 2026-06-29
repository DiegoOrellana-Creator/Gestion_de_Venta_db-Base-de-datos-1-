from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from uuid import uuid4
from database.db import get_connection


@dataclass
class DetalleVenta:
    id: str = field(default_factory=lambda: str(uuid4()))
    venta_id: str = ""
    producto_id: str = ""
    cantidad: int = 1
    precio_unitario: float = 0.0
    subtotal: float = 0.0
    producto_nombre: str = ""


@dataclass
class Venta:
    id_venta: str = field(default_factory=lambda: str(uuid4()))
    cliente_id: str = ""
    vendedor_id: str = ""
    fecha: str = ""
    total: float = 0.0
    metodo_pago: str = "Efectivo"
    estado: str = "Completada"
    # joined
    cliente_nombre: str = ""
    vendedor_nombre: str = ""
    detalles: List[DetalleVenta] = field(default_factory=list)

    @staticmethod
    def get_all(limit=200):
        conn = get_connection()
        rows = conn.execute("""
            SELECT v.id_venta, v.cliente_id, v.vendedor_id, v.fecha,
                   v.total, v.metodo_pago, v.estado,
                   pc.nombre AS cliente_nombre,
                   pv.nombre AS vendedor_nombre
            FROM ventas v
            JOIN clientes  cl ON cl.id = v.cliente_id
            JOIN roles     rc ON rc.id = cl.id
            JOIN personas  pc ON pc.id = rc.persona_id
            JOIN vendedores vd ON vd.id = v.vendedor_id
            JOIN roles      rv ON rv.id = vd.id
            JOIN personas   pv ON pv.id = rv.persona_id
            ORDER BY v.fecha DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [Venta(**{k: v for k, v in dict(r).items()}) for r in rows]

    @staticmethod
    def get_by_id(vid: str) -> Optional['Venta']:
        conn = get_connection()
        r = conn.execute("""
            SELECT v.id_venta, v.cliente_id, v.vendedor_id, v.fecha,
                   v.total, v.metodo_pago, v.estado,
                   pc.nombre AS cliente_nombre,
                   pv.nombre AS vendedor_nombre
            FROM ventas v
            JOIN clientes  cl ON cl.id = v.cliente_id
            JOIN roles     rc ON rc.id = cl.id
            JOIN personas  pc ON pc.id = rc.persona_id
            JOIN vendedores vd ON vd.id = v.vendedor_id
            JOIN roles      rv ON rv.id = vd.id
            JOIN personas   pv ON pv.id = rv.persona_id
            WHERE v.id_venta=?
        """, (vid,)).fetchone()
        if not r:
            conn.close(); return None
        venta = Venta(**{k: v for k, v in dict(r).items()})
        rows_d = conn.execute("""
            SELECT d.id, d.venta_id, d.producto_id, d.cantidad,
                   d.precio_unitario, d.subtotal, p.nombre AS producto_nombre
            FROM detalle_ventas d
            JOIN productos p ON p.id_producto = d.producto_id
            WHERE d.venta_id=?
        """, (vid,)).fetchall()
        venta.detalles = [DetalleVenta(**dict(rd)) for rd in rows_d]
        conn.close()
        return venta

    @staticmethod
    def get_by_date(day: str, limit=500):
        conn = get_connection()
        rows = conn.execute("""
            SELECT v.id_venta, v.cliente_id, v.vendedor_id, v.fecha,
                   v.total, v.metodo_pago, v.estado,
                   pc.nombre AS cliente_nombre,
                   pv.nombre AS vendedor_nombre
            FROM ventas v
            JOIN clientes  cl ON cl.id = v.cliente_id
            JOIN roles     rc ON rc.id = cl.id
            JOIN personas  pc ON pc.id = rc.persona_id
            JOIN vendedores vd ON vd.id = v.vendedor_id
            JOIN roles      rv ON rv.id = vd.id
            JOIN personas   pv ON pv.id = rv.persona_id
            WHERE date(v.fecha)=?
            ORDER BY v.fecha DESC
            LIMIT ?
        """, (day, limit)).fetchall()
        conn.close()
        return [Venta(**{k: v for k, v in dict(r).items()}) for r in rows]

    def save(self):
        """Persiste la venta completa y descuenta stock."""
        conn = get_connection()
        conn.execute("""
            INSERT INTO ventas(id_venta,cliente_id,vendedor_id,total,metodo_pago,estado)
            VALUES (?,?,?,?,?,?)
        """, (self.id_venta, self.cliente_id, self.vendedor_id,
              self.total, self.metodo_pago, self.estado))
        for d in self.detalles:
            d.venta_id = self.id_venta
            conn.execute("""
                INSERT INTO detalle_ventas(id,venta_id,producto_id,cantidad,precio_unitario,subtotal)
                VALUES (?,?,?,?,?,?)
            """, (d.id, d.venta_id, d.producto_id, d.cantidad,
                  d.precio_unitario, d.subtotal))
            # Descontar stock
            conn.execute("""
                UPDATE stock_ubicacion SET cantidad = cantidad - ?
                WHERE id = (
                    SELECT id FROM stock_ubicacion
                    WHERE producto_id=? AND cantidad >= ?
                    LIMIT 1
                )
            """, (d.cantidad, d.producto_id, d.cantidad))
        conn.commit(); conn.close()

    def anular(self):
        conn = get_connection()
        conn.execute("UPDATE ventas SET estado='Anulada' WHERE id_venta=?", (self.id_venta,))
        # Revertir stock
        for d in self.detalles:
            conn.execute("""
                UPDATE stock_ubicacion SET cantidad = cantidad + ?
                WHERE id = (
                    SELECT id FROM stock_ubicacion
                    WHERE producto_id=? LIMIT 1
                )
            """, (d.cantidad, d.producto_id))
        conn.commit(); conn.close()
        self.estado = 'Anulada'

    @staticmethod
    def resumen_dashboard(day: str | None = None):
        fecha = day if day else date.today().isoformat()
        conn = get_connection()
        r = conn.execute("""
            SELECT
                COUNT(*)                                         AS total_ventas,
                COALESCE(SUM(total),0)                           AS ingresos_totales,
                COALESCE(AVG(total),0)                           AS ticket_promedio,
                COUNT(CASE WHEN estado='Anulada' THEN 1 END)     AS anuladas
            FROM ventas
            WHERE date(fecha)=?
        """, (fecha,)).fetchone()
        top = conn.execute("""
            SELECT p.nombre, SUM(d.cantidad) AS qty
            FROM detalle_ventas d
            JOIN productos p ON p.id_producto = d.producto_id
            JOIN ventas v ON v.id_venta = d.venta_id
            WHERE date(v.fecha)=?
            GROUP BY d.producto_id ORDER BY qty DESC LIMIT 5
        """, (fecha,)).fetchall()
        conn.close()
        return dict(r), [dict(t) for t in top]
