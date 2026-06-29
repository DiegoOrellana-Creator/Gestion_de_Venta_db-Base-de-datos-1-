from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4
from database.db import get_connection


# ─────────────────────────────────────────────────────────────
# PERSONA
# ─────────────────────────────────────────────────────────────
@dataclass
class Persona:
    id: str = field(default_factory=lambda: str(uuid4()))
    nombre: str = ""
    email: str = ""
    password: str = ""
    telefono: str = ""
    direccion: str = ""
    sexo: str = "M"
    creado_at: str = ""

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM personas ORDER BY nombre").fetchall()
        conn.close()
        return [Persona(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(pid: str) -> Optional['Persona']:
        conn = get_connection()
        r = conn.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone()
        conn.close()
        return Persona(**dict(r)) if r else None

    @staticmethod
    def get_by_email(email: str) -> Optional['Persona']:
        conn = get_connection()
        r = conn.execute("SELECT * FROM personas WHERE email=?", (email,)).fetchone()
        conn.close()
        return Persona(**dict(r)) if r else None

    def save(self):
        conn = get_connection()
        conn.execute("""
            INSERT INTO personas(id,nombre,email,password,telefono,direccion,sexo)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                nombre=excluded.nombre, email=excluded.email, password=excluded.password,
                telefono=excluded.telefono, direccion=excluded.direccion,
                sexo=excluded.sexo
        """, (self.id, self.nombre, self.email, self.password, self.telefono, self.direccion, self.sexo))
        conn.commit(); conn.close()

    def delete(self):
        conn = get_connection()
        conn.execute("DELETE FROM personas WHERE id=?", (self.id,))
        conn.commit(); conn.close()


# ─────────────────────────────────────────────────────────────
# ROL
# ─────────────────────────────────────────────────────────────
@dataclass
class Rol:
    id: str = field(default_factory=lambda: str(uuid4()))
    persona_id: str = ""
    tipo: str = "Cliente"
    fecha_asignada: str = ""
    activo: int = 1

    @staticmethod
    def get_by_persona(persona_id: str):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM roles WHERE persona_id=?", (persona_id,)).fetchall()
        conn.close()
        return [Rol(**dict(r)) for r in rows]

    def save(self):
        conn = get_connection()
        conn.execute("""
            INSERT INTO roles(id,persona_id,tipo,activo) VALUES (?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET activo=excluded.activo
        """, (self.id, self.persona_id, self.tipo, self.activo))
        conn.commit(); conn.close()


# ─────────────────────────────────────────────────────────────
# CLIENTE (join con persona vía rol)
# ─────────────────────────────────────────────────────────────
@dataclass
class Cliente:
    id: str = ""           # = roles.id
    persona_id: str = ""
    nombre: str = ""
    email: str = ""
    telefono: str = ""
    puntos: int = 0
    credito: float = 0.00

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT c.id, r.persona_id, p.nombre, p.email, p.telefono,
                   c.puntos, c.credito
            FROM clientes c
            JOIN roles    r ON r.id = c.id
            JOIN personas p ON p.id = r.persona_id
            WHERE r.activo = 1
            ORDER BY p.nombre
        """).fetchall()
        conn.close()
        return [Cliente(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(cid: str) -> Optional['Cliente']:
        conn = get_connection()
        r = conn.execute("""
            SELECT c.id, r.persona_id, p.nombre, p.email, p.telefono,
                   c.puntos, c.credito
            FROM clientes c
            JOIN roles    r ON r.id = c.id
            JOIN personas p ON p.id = r.persona_id
            WHERE c.id=?
        """, (cid,)).fetchone()
        conn.close()
        return Cliente(**dict(r)) if r else None

    def add_puntos(self, pts: int):
        conn = get_connection()
        conn.execute("UPDATE clientes SET puntos = puntos + ? WHERE id=?", (pts, self.id))
        conn.commit(); conn.close()
        self.puntos += pts


# ─────────────────────────────────────────────────────────────
# VENDEDOR
# ─────────────────────────────────────────────────────────────
@dataclass
class Vendedor:
    id: str = ""
    persona_id: str = ""
    nombre: str = ""
    email: str = ""
    codigo: str = ""
    comision: float = 0.00

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT v.id, r.persona_id, p.nombre, p.email,
                   v.codigo, v.comision
            FROM vendedores v
            JOIN roles    r ON r.id = v.id
            JOIN personas p ON p.id = r.persona_id
            WHERE r.activo = 1
            ORDER BY p.nombre
        """).fetchall()
        conn.close()
        return [Vendedor(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(vid: str) -> Optional['Vendedor']:
        conn = get_connection()
        r = conn.execute("""
            SELECT v.id, r.persona_id, p.nombre, p.email,
                   v.codigo, v.comision
            FROM vendedores v
            JOIN roles    r ON r.id = v.id
            JOIN personas p ON p.id = r.persona_id
            WHERE v.id=?
        """, (vid,)).fetchone()
        conn.close()
        return Vendedor(**dict(r)) if r else None
