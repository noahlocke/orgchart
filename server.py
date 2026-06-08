#!/usr/bin/env python3
"""Minimal dev server: static files from project root + POST /dist/save."""
import http.server, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / 'dist'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == '/dist/save':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length))
                filename = os.path.basename(body.get('filename', 'orgchart-edited')) + '.html'
                DIST.mkdir(exist_ok=True)
                (DIST / filename).write_text(body['content'], encoding='utf-8')
                self.send_response(200)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'file': filename}).encode())
            except Exception as e:
                self.send_response(500)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        pass  # quiet

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7891
    print(f'Serving on http://localhost:{port}')
    with http.server.HTTPServer(('', port), Handler) as s:
        s.serve_forever()
