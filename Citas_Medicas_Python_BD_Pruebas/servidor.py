from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from urllib.parse import urlparse
from database import initialize
from reservas import reservar, listar_citas, ReservaError

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(Path(__file__).parent),**kwargs)
    def do_GET(self):
        if urlparse(self.path).path == '/api/citas':
            return self.respond(200, {'citas':listar_citas()})
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path != '/api/citas': return self.respond(404,{'error':'Ruta no encontrada'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length > 10000: return self.respond(413,{'error':'Solicitud demasiado grande'})
            datos=json.loads(self.rfile.read(length))
            if not isinstance(datos,dict): raise ValueError('Se requiere un objeto JSON')
            return self.respond(201,{'cita':reservar(datos)})
        except (ReservaError,ValueError,UnicodeDecodeError) as exc:
            return self.respond(400,{'error':str(exc)})
    def respond(self,status,body):
        payload=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers();self.wfile.write(payload)

if __name__ == '__main__':
    initialize()
    print('Abre http://localhost:8000/sistema_citas_medicas.html')
    ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
