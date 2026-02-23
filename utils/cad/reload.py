import socket
import json
from pathlib import Path

def reload(path: str | Path, print_response: bool=False):
    '''Sends klive a request to reload the gds file at `path`'''
    path = Path(path)
    data = { 
        "gds": str(path.resolve())
    }

    package = json.dumps(data)
    package += '\n'

    try:
        conn = socket.socket()
        conn.settimeout(0.5)
        conn.connect(('localhost', 8082))
        conn.sendall(package.encode())
        conn.settimeout(1)

        received = conn.recv(1024).decode("utf-8")
    except ConnectionRefusedError as e:
        raise ConnectionRefusedError('Is klayout open?') from e
    finally:
        conn.close()
    if print_response:
        print('Response from klayout:')
        print(received)
