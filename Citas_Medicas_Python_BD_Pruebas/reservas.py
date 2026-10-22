import re
import sqlite3
from datetime import datetime, date, time
from database import connect, initialize, DB_PATH

class ReservaError(ValueError): pass

def validar_nombre(nombre):
    return isinstance(nombre,str) and bool(re.fullmatch(r'[^\W\d_]+(?: +[^\W\d_]+)*',nombre.strip(),re.UNICODE))

def validar_fecha_hora(fecha, hora, ahora=None):
    ahora = ahora or datetime.now()
    try:
        f = date.fromisoformat(fecha)
        h = time.fromisoformat(hora)
    except (ValueError,TypeError):
        raise ReservaError('Fecha u hora inválida.')
    if f < ahora.date(): raise ReservaError('No se permiten citas para fechas pasadas.')
    if not time(8,0) <= h <= time(17,0):
        raise ReservaError('El horario permitido es de 8:00 a. m. a 5:00 p. m.')
    if datetime.combine(f,h) <= ahora:
        raise ReservaError('Seleccione una fecha y hora futuras.')
    return True

def reservar(datos, path=DB_PATH, ahora=None):
    nombre = datos.get('patient')
    if not validar_nombre(nombre):
        raise ReservaError('El nombre es obligatorio y solo puede contener letras y espacios.')
    validar_fecha_hora(datos.get('date'),datos.get('time'),ahora)
    especialidad, medico = datos.get('specialty'), datos.get('doctor')
    with connect(path) as con:
        fila=con.execute('SELECT id FROM medicos WHERE nombre=? AND especialidad=?',(medico,especialidad)).fetchone()
        if not fila: raise ReservaError('Seleccione un médico válido para la especialidad.')
        try:
            # La restricción UNIQUE impide duplicados incluso entre solicitudes concurrentes.
            con.execute('BEGIN IMMEDIATE')
            cur=con.execute('INSERT INTO pacientes(nombre) VALUES (?)',(nombre.strip(),))
            cur2=con.execute('INSERT INTO citas(paciente_id,medico_id,fecha,hora) VALUES (?,?,?,?)',
                (cur.lastrowid,fila['id'],datos['date'],datos['time']))
            return {'id':cur2.lastrowid,'patient':nombre.strip(),'specialty':especialidad,
                    'doctor':medico,'date':datos['date'],'time':datos['time']}
        except sqlite3.IntegrityError as exc:
            raise ReservaError('Este médico ya tiene una cita en esa fecha y hora.') from exc

def listar_citas(path=DB_PATH):
    with connect(path) as con:
        return [dict(row) for row in con.execute("""SELECT c.id,p.nombre AS patient,m.nombre AS doctor,
            m.especialidad AS specialty,c.fecha AS date,c.hora AS time
            FROM citas c JOIN pacientes p ON p.id=c.paciente_id
            JOIN medicos m ON m.id=c.medico_id ORDER BY c.fecha,c.hora""")]
