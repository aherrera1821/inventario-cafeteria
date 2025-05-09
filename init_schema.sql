CREATE TABLE IF NOT EXISTS insumos (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    unidad TEXT NOT NULL,
    cantidad_actual REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS movimientos (
    id SERIAL PRIMARY KEY,
    tipo TEXT CHECK (tipo IN ('entrada', 'salida')) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insumo_id INTEGER REFERENCES insumos(id),
    cantidad REAL NOT NULL,
    observacion TEXT
);
