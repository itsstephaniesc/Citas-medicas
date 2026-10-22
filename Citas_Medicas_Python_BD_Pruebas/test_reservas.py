import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from database import initialize, connect
from reservas import validar_nombre, validar_fecha_hora, reservar, listar_citas, ReservaError

class PruebasReservas(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Path(self.tmp.name)/'pruebas.db'
        initialize(self.db)
        self.ahora=datetime(2026,10,21,9,0)
        self.datos={'patient':'AÑADIR NOMBRE','specialty':'Cardiología','doctor':'Dr. ','date':'2026-10-22','time':'10:00'}
    def tearDown(self): self.tmp.cleanup()
    def guardar(self,**cambios): return reservar({**self.datos,**cambios},self.db,self.ahora)
    def test_01_nombre_valido(self): self.assertTrue(validar_nombre('María Rodríguez'))
    def test_02_nombre_vacio(self): self.assertFalse(validar_nombre(''))
    def test_03_nombre_espacios(self): self.assertFalse(validar_nombre('   '))
    def test_04_nombre_numeros(self): self.assertFalse(validar_nombre('Ana123'))
    def test_05_nombre_simbolos(self): self.assertFalse(validar_nombre('Ana@'))
    def test_06_fecha_pasada(self):
        with self.assertRaises(ReservaError): self.guardar(date='2026-10-20')
    def test_07_hora_antes_ocho(self):
        with self.assertRaises(ReservaError): self.guardar(time='07:59')
    def test_08_hora_despues_cinco(self):
        with self.assertRaises(ReservaError): self.guardar(time='17:01')
    def test_09_limite_ocho(self): self.assertTrue(self.guardar(time='08:00')['id'])
    def test_10_limite_cinco(self): self.assertTrue(self.guardar(time='17:00')['id'])
    def test_11_fecha_hoy_hora_pasada(self):
        with self.assertRaises(ReservaError): self.guardar(date='2026-10-21',time='08:00')
    def test_12_fecha_hoy_hora_futura(self): self.assertTrue(self.guardar(date='2026-10-21',time='10:00')['id'])
    def test_13_fecha_invalida(self):
        with self.assertRaises(ReservaError): self.guardar(date='2026-02-30')
    def test_14_especialidad_medico_incorrectos(self):
        with self.assertRaises(ReservaError): self.guardar(specialty='Pediatría')
    def test_15_reserva_exitosa(self): self.assertEqual(len(listar_citas(self.db)) if not self.guardar() else len(listar_citas(self.db)),1)
    def test_16_duplicado_mismo_medico(self):
        self.guardar()
        with self.assertRaises(ReservaError): self.guardar(patient='Ana Mora')
    def test_17_medicos_distintos_misma_hora(self):
        self.guardar(); self.guardar(doctor='Dra. Sofía Rojas')
        self.assertEqual(len(listar_citas(self.db)),2)
    def test_18_mismo_medico_otra_hora(self):
        self.guardar();self.guardar(time='11:00')
        self.assertEqual(len(listar_citas(self.db)),2)
    def test_19_persistencia_sqlite(self):
        self.guardar()
        with connect(self.db) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM citas').fetchone()[0],1)
    def test_20_duplicado_no_crea_paciente_huerfano(self):
        self.guardar()
        with self.assertRaises(ReservaError): self.guardar(patient='Otra Persona')
        with connect(self.db) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM pacientes').fetchone()[0],1)
    def test_21_nombre_invalido_no_guarda(self):
        with self.assertRaises(ReservaError): self.guardar(patient='Ana99')
        self.assertEqual(len(listar_citas(self.db)),0)
    def test_22_sql_injection_nombre_rechazado(self):
        with self.assertRaises(ReservaError): self.guardar(patient="Ana'; DROP TABLE citas;--")
        with connect(self.db) as con: self.assertIsNotNone(con.execute("SELECT name FROM sqlite_master WHERE name='citas'").fetchone())

if __name__=='__main__': unittest.main(verbosity=2)
