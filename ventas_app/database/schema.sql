PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
-- ─── PERSONAS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS personas (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    telefono TEXT,
    direccion TEXT,
    sexo TEXT CHECK(sexo IN ('M', 'F', 'O')),
    creado_at TEXT DEFAULT (datetime('now'))
);
-- ─── ROLES ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    persona_id TEXT NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK(tipo IN ('Dueño', 'Vendedor', 'Cliente')),
    fecha_asignada TEXT DEFAULT (datetime('now')),
    activo INTEGER DEFAULT 1 -- 1=TRUE, 0=FALSE
);
-- ─── ESPECIALIZACIONES DE ROL ────────────────────────────────
CREATE TABLE IF NOT EXISTS clientes (
    id TEXT PRIMARY KEY REFERENCES roles(id) ON DELETE CASCADE,
    puntos INTEGER DEFAULT 0,
    credito REAL DEFAULT 0.00
);
CREATE TABLE IF NOT EXISTS vendedores (
    id TEXT PRIMARY KEY REFERENCES roles(id) ON DELETE CASCADE,
    codigo TEXT UNIQUE NOT NULL,
    comision REAL DEFAULT 0.00
);
CREATE TABLE IF NOT EXISTS duenos (
    id TEXT PRIMARY KEY REFERENCES roles(id) ON DELETE CASCADE
);
-- ─── UBICACIONES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tiendas (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    direccion TEXT NOT NULL,
    capacidad INTEGER
);
CREATE TABLE IF NOT EXISTS almacenes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    direccion TEXT NOT NULL,
    capacidad INTEGER
);
-- ─── PRODUCTOS ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tipo_calzado (
    id_tipo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS productos (
    id_producto TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    descuento REAL NOT NULL DEFAULT 0.0,
    activo INTEGER DEFAULT 1,
    fecha_registro TEXT DEFAULT (datetime('now')),
    marca TEXT,
    tipo_producto TEXT NOT NULL CHECK(tipo_producto IN ('Mochila', 'Calzado', 'Pelota'))
);
CREATE TABLE IF NOT EXISTS mochilas (
    id_producto TEXT PRIMARY KEY REFERENCES productos(id_producto) ON DELETE CASCADE,
    material TEXT,
    num_compartimiento INTEGER,
    color TEXT
);
CREATE TABLE IF NOT EXISTS calzados (
    id_producto TEXT PRIMARY KEY REFERENCES productos(id_producto) ON DELETE CASCADE,
    talla REAL,
    material TEXT,
    genero TEXT,
    color TEXT,
    tipo_id TEXT REFERENCES tipo_calzado(id_tipo) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS pelotas (
    id_producto TEXT PRIMARY KEY REFERENCES productos(id_producto) ON DELETE CASCADE,
    deporte TEXT,
    numero INTEGER,
    infable_bool INTEGER DEFAULT 1
);
-- ─── STOCK ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stock_ubicacion (
    id TEXT PRIMARY KEY,
    tienda_id TEXT REFERENCES tiendas(id) ON DELETE CASCADE,
    almacen_id TEXT REFERENCES almacenes(id) ON DELETE CASCADE,
    producto_id TEXT NOT NULL REFERENCES productos(id_producto) ON DELETE CASCADE,
    cantidad INTEGER NOT NULL DEFAULT 0 CHECK(cantidad >= 0),
    fecha_ingreso TEXT DEFAULT (datetime('now')),
    CHECK(
        tienda_id IS NOT NULL
        OR almacen_id IS NOT NULL
    )
);
-- ─── VENTAS ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ventas (
    id_venta TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    vendedor_id TEXT NOT NULL REFERENCES vendedores(id) ON DELETE RESTRICT,
    fecha TEXT NOT NULL DEFAULT (datetime('now')),
    total REAL NOT NULL DEFAULT 0.00,
    metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('Efectivo', 'Tarjeta', 'QR')),
    estado TEXT NOT NULL DEFAULT 'Completada' CHECK(estado IN ('Completada', 'Anulada'))
);
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id TEXT PRIMARY KEY,
    venta_id TEXT NOT NULL REFERENCES ventas(id_venta) ON DELETE CASCADE,
    producto_id TEXT NOT NULL REFERENCES productos(id_producto) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    precio_unitario REAL NOT NULL,
    subtotal REAL NOT NULL
);
-- ─── ÍNDICES ─────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_stock_producto ON stock_ubicacion(producto_id);
CREATE INDEX IF NOT EXISTS idx_detalle_venta ON detalle_ventas(venta_id);
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre);
CREATE INDEX IF NOT EXISTS idx_roles_persona ON roles(persona_id);