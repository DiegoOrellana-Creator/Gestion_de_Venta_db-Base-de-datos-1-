
import os
from uuid import uuid4
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from models.venta import Venta, DetalleVenta
from models.producto import Producto, StockUbicacion
from models.persona import Cliente, Vendedor, Persona, Rol


# ─────────────────────────────────────────────────────────────
# VENTA CONTROLLER
# ─────────────────────────────────────────────────────────────
class VentaController:

    @staticmethod
    def listar_ventas():
        return Venta.get_all()

    @staticmethod
    def obtener_venta(vid: str):
        return Venta.get_by_id(vid)

    @staticmethod
    def obtener_ventas_por_dia(fecha: str):
        return Venta.get_by_date(fecha)

    @staticmethod
    def generar_reporte_dia(fecha: str, path: str) -> tuple[bool, str]:
        ventas = Venta.get_by_date(fecha)
        if not ventas:
            return False, "No se encontraron ventas para esa fecha."
        try:
            if not path.lower().endswith('.pdf'):
                path += '.pdf'
            os.makedirs(os.path.dirname(path), exist_ok=True)
            total_ingresos = sum(v.total for v in ventas)
            c = canvas.Canvas(path, pagesize=A4)
            width, height = A4
            margin = 20 * mm
            x = margin
            y = height - margin

            c.setFont('Helvetica-Bold', 14)
            c.drawString(x, y, f'REPORTE DE VENTAS - {fecha}')
            y -= 12 * mm

            c.setFont('Helvetica', 11)
            c.drawString(x, y, f'Ventas totales: {len(ventas)}')
            y -= 6 * mm
            c.drawString(x, y, f'Ingresos totales: Bs. {total_ingresos:,.2f}')
            y -= 6 * mm
            c.drawString(x, y, '========================================')
            y -= 8 * mm

            for v in ventas:
                if y < margin + 40:
                    c.showPage()
                    y = height - margin
                    c.setFont('Helvetica', 11)
                c.setFont('Helvetica-Bold', 11)
                c.drawString(x, y, f'Venta: {v.id_venta}')
                y -= 6 * mm
                c.setFont('Helvetica', 10)
                c.drawString(x, y, f'Fecha: {v.fecha}')
                y -= 5 * mm
                c.drawString(x, y, f'Cliente: {v.cliente_nombre}')
                y -= 5 * mm
                c.drawString(x, y, f'Vendedor: {v.vendedor_nombre}')
                y -= 5 * mm
                c.drawString(x, y, f'Método: {v.metodo_pago}')
                y -= 5 * mm
                c.drawString(x, y, f'Estado: {v.estado}')
                y -= 5 * mm
                c.drawString(x, y, f'Total: Bs. {v.total:,.2f}')
                y -= 6 * mm
                c.drawString(x, y, 'Detalle:')
                y -= 5 * mm
                venta_detalle = Venta.get_by_id(v.id_venta)
                if venta_detalle and venta_detalle.detalles:
                    for d in venta_detalle.detalles:
                        if y < margin + 30:
                            c.showPage()
                            y = height - margin
                            c.setFont('Helvetica', 10)
                        c.drawString(x + 10, y, f'{d.producto_nombre} | Qty: {d.cantidad} | Precio: Bs. {d.precio_unitario:,.2f} | Subtotal: Bs. {d.subtotal:,.2f}')
                        y -= 5 * mm
                else:
                    c.drawString(x + 10, y, '(sin detalles)')
                    y -= 5 * mm
                c.drawString(x, y, '----------------------------------------')
                y -= 8 * mm

            c.save()
            return True, f'Reporte PDF guardado en:\n{path}'
        except Exception as e:
            return False, str(e)

    @staticmethod
    def crear_venta(cliente_id: str, vendedor_id: str,
                    metodo_pago: str, items: list) -> tuple[bool, str, Venta | None]:
        """
        items = [{'producto_id': str, 'cantidad': int, 'precio_unitario': float}, ...]
        Retorna (ok, mensaje, venta)
        """
        if not items:
            return False, "La venta no tiene productos.", None

        # Validar stock suficiente
        for item in items:
            prod = Producto.get_by_id(item['producto_id'])
            if not prod:
                return False, f"Producto no encontrado: {item['producto_id']}", None
            if prod.stock_total < item['cantidad']:
                return False, f"Stock insuficiente para '{prod.nombre}' (disponible: {prod.stock_total})", None

        total = sum(i['cantidad'] * i['precio_unitario'] for i in items)
        venta = Venta(
            id_venta=str(uuid4()),
            cliente_id=cliente_id,
            vendedor_id=vendedor_id,
            total=round(total, 2),
            metodo_pago=metodo_pago,
            estado='Completada'
        )
        for item in items:
            prod = Producto.get_by_id(item['producto_id'])
            subtotal = round(item['cantidad'] * item['precio_unitario'], 2)
            venta.detalles.append(DetalleVenta(
                id=str(uuid4()),
                producto_id=item['producto_id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'],
                subtotal=subtotal,
                producto_nombre=prod.nombre if prod else ""
            ))

        venta.save()
        # Sumar puntos al cliente (1 punto por Bs.)
        cliente = Cliente.get_by_id(cliente_id)
        if cliente:
            cliente.add_puntos(int(total))
        return True, "Venta registrada correctamente.", venta

    @staticmethod
    def anular_venta(vid: str) -> tuple[bool, str]:
        venta = Venta.get_by_id(vid)
        if not venta:
            return False, "Venta no encontrada."
        if venta.estado == 'Anulada':
            return False, "La venta ya está anulada."
        venta.anular()
        return True, "Venta anulada y stock revertido."

    @staticmethod
    def dashboard(day: str | None = None):
        return Venta.resumen_dashboard(day)


# ─────────────────────────────────────────────────────────────
# PRODUCTO CONTROLLER
# ─────────────────────────────────────────────────────────────
class ProductoController:

    @staticmethod
    def listar(busqueda=""):
        if busqueda:
            return Producto.search(busqueda)
        return Producto.get_all()

    @staticmethod
    def guardar(data: dict) -> tuple[bool, str]:
        try:
            precio = float(data.get('precio', 0))
            descuento = float(data.get('descuento', 0) or 0)
            if precio <= 0:
                return False, "El precio debe ser mayor a 0."
            if descuento < 0 or descuento > 100:
                return False, "El descuento debe estar entre 0 y 100%."
            if not data.get('nombre', '').strip():
                return False, "El nombre es obligatorio."
            stock_val = data.get('stock', '').strip()
            stock = 0
            if stock_val:
                try:
                    stock = int(stock_val)
                except ValueError:
                    return False, "El stock debe ser un número entero."
                if stock < 0:
                    return False, "El stock no puede ser negativo."

            prod = Producto(
                id_producto=data.get('id_producto') or str(uuid4()),
                nombre=data['nombre'].strip(),
                precio=precio,
                descuento=descuento,
                marca=data.get('marca', '').strip(),
                tipo_producto=data.get('tipo_producto', 'Mochila'),
                activo=1
            )
            prod.save()

            if stock_val != '':
                from database.db import get_connection
                conn = get_connection()
                row = conn.execute(
                    "SELECT id FROM stock_ubicacion WHERE producto_id=? LIMIT 1",
                    (prod.id_producto,)
                ).fetchone()
                conn.close()
                if row:
                    stock_item = StockUbicacion(id=row['id'], producto_id=prod.id_producto, cantidad=stock)
                    stock_item.save()
                else:
                    from database.db import get_connection as gc
                    conn2 = gc()
                    tienda = conn2.execute("SELECT id FROM tiendas LIMIT 1").fetchone()
                    conn2.close()
                    if not tienda:
                        return False, "No hay tienda disponible para asignar stock."
                    stock_item = StockUbicacion(tienda_id=tienda['id'], producto_id=prod.id_producto, cantidad=stock)
                    stock_item.save()
            return True, "Producto guardado."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def eliminar(pid: str) -> tuple[bool, str]:
        prod = Producto.get_by_id(pid)
        if not prod:
            return False, "Producto no encontrado."
        prod.delete()
        return True, "Producto desactivado."

    @staticmethod
    def listar_stock():
        return StockUbicacion.get_all()


# ─────────────────────────────────────────────────────────────
# CLIENTE CONTROLLER
# ─────────────────────────────────────────────────────────────
class ClienteController:

    @staticmethod
    def listar():
        return Cliente.get_all()

    @staticmethod
    def guardar(data: dict) -> tuple[bool, str]:
        try:
            from database.db import get_connection
            conn = get_connection()
            # Verificar email único
            existe = conn.execute(
                "SELECT id FROM personas WHERE email=? AND id!=?",
                (data['email'], data.get('persona_id', ''))
            ).fetchone()
            conn.close()
            if existe:
                return False, "El email ya está registrado."

            persona = Persona(
                id=data.get('persona_id') or str(uuid4()),
                nombre=data['nombre'].strip(),
                email=data['email'].strip(),
                password=data.get('password','').strip(),
                telefono=data.get('telefono', '').strip(),
                sexo=data.get('sexo', 'M')
            )
            persona.save()

            if not data.get('rol_id'):
                rol = Rol(id=str(uuid4()), persona_id=persona.id, tipo='Cliente')
                rol.save()
                rol_id = rol.id
                from database.db import get_connection as gc
                c = gc()
                c.execute("INSERT OR IGNORE INTO clientes(id,puntos,credito) VALUES (?,0,0.00)", (rol_id,))
                c.commit(); c.close()
            return True, "Cliente guardado."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def eliminar(cid: str) -> tuple[bool, str]:
        cliente = Cliente.get_by_id(cid)
        if not cliente:
            return False, "Cliente no encontrado."
        try:
            from database.db import get_connection
            conn = get_connection()
            conn.execute("UPDATE roles SET activo=0 WHERE id=?", (cid,))
            conn.commit(); conn.close()
            return True, "Cliente eliminado."
        except Exception as e:
            return False, str(e)


# ─────────────────────────────────────────────────────────────
# VENDEDOR CONTROLLER
# ─────────────────────────────────────────────────────────────
class VendedorController:

    @staticmethod
    def listar():
        return Vendedor.get_all()

    @staticmethod
    def guardar(data: dict) -> tuple[bool, str]:
        try:
            from database.db import get_connection
            if not data.get('codigo', '').strip():
                return False, "El código de vendedor es obligatorio."
            conn = get_connection()
            existe = conn.execute(
                "SELECT id FROM vendedores WHERE codigo=?", (data['codigo'],)
            ).fetchone()
            conn.close()
            if existe and existe['id'] != data.get('rol_id', ''):
                return False, "El código de vendedor ya existe."

            password = data.get('password', '').strip()
            if data.get('persona_id') and not password:
                existing = Persona.get_by_id(data['persona_id'])
                password = existing.password if existing else ''

            persona = Persona(
                id=data.get('persona_id') or str(uuid4()),
                nombre=data['nombre'].strip(),
                email=data['email'].strip(),
                password=password,
                telefono=data.get('telefono', '').strip(),
                sexo=data.get('sexo', 'M')
            )
            persona.save()

            if not data.get('rol_id'):
                rol = Rol(id=str(uuid4()), persona_id=persona.id, tipo='Vendedor')
                rol.save()
                c = get_connection()
                c.execute("INSERT OR IGNORE INTO vendedores(id,codigo,comision) VALUES (?,?,?)",
                          (rol.id, data['codigo'], float(data.get('comision', 0))))
                c.commit(); c.close()
            return True, "Vendedor guardado."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def eliminar(vid: str) -> tuple[bool, str]:
        try:
            from database.db import get_connection
            v = Vendedor.get_by_id(vid)
            if not v:
                return False, "Vendedor no encontrado."
            c = get_connection()
            # marcar rol como inactivo
            c.execute("UPDATE roles SET activo=0 WHERE id=?", (vid,))
            # eliminar fila de vendedores (opcional)
            c.execute("DELETE FROM vendedores WHERE id=?", (vid,))
            c.commit(); c.close()
            return True, "Vendedor eliminado."
        except Exception as e:
            return False, str(e)


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────
class AuthController:
    @staticmethod
    def authenticate(email: str, password: str) -> tuple[bool, str, Persona | None, Rol | None]:
        try:
            from database.db import get_connection
            conn = get_connection()
            r = conn.execute("SELECT * FROM personas WHERE email=?", (email,)).fetchone()
            if not r:
                conn.close()
                return False, "Email no registrado.", None, None
            persona = Persona(**dict(r))
            # verificar contraseña
            if (persona.password or "") != password:
                conn.close()
                return False, "Contraseña incorrecta.", None, None
            role_row = conn.execute(
                "SELECT * FROM roles WHERE persona_id=? AND activo=1 AND tipo IN ('Dueño','Vendedor')",
                (persona.id,)
            ).fetchone()
            conn.close()
            if not role_row:
                return False, "No tienes un rol activo para acceder.", None, None
            rol = Rol(**dict(role_row))
            return True, "Autenticado.", persona, rol
        except Exception as e:
            return False, str(e), None, None
