import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).with_name('citas_medicas.db')
MEDICOS = {

 
}
def connect(path=DB_PATH):
    con = sqlite3.connect(str(path), timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def initialize(path=DB_PATH):
    with connect(path) as con:
        con.executescript("""CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL CHECK(length(trim(nombre)) > 0));
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            especialidad TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
            medico_id INTEGER NOT NULL REFERENCES medicos(id),
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(medico_id, fecha, hora));""")
        for especialidad, nombres in MEDICOS.items():
            for nombre in nombres:
                con.execute('INSERT OR IGNORE INTO medicos(nombre, especialidad) VALUES (?,?)',(nombre,especialidad))
