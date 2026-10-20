import argparse
import http.client
import re
import socket
import time
from decimal import Decimal, getcontext

parser = argparse.ArgumentParser(description='Follow the authorized lab port sequence')
parser.add_argument('host', help='Current TryHackMe task machine IP')
args = parser.parse_args()
getcontext().prec = 100

def fetch(port):
    with socket.create_connection((args.host, port), timeout=1) as sock:
        sock.sendall((f'GET / HTTP/1.1\r\nHost: {args.host}:{port}\r\n'
                      'Connection: close\r\n\r\n').encode())
        response = http.client.HTTPResponse(sock)
        response.begin()
        return response.read().decode('utf-8', errors='replace')

port, total = 1337, Decimal('0')
print('Waiting for port 1337. Ctrl+C to stop.')
while port != 9765:
    try:
        body = fetch(port)
    except (OSError, http.client.HTTPException):
        time.sleep(0.1)
        continue
    text = re.sub(r'<[^>]*>', ' ', body).strip()
    if text.upper() == 'STOP':
        break
    match = re.search(r'\b(add|minus|multiply|divide)\s+(-?\d+(?:\.\d+)?)\s+(\d+)\b', text, re.I)
    if not match:
        raise SystemExit(f'Unexpected response on {port}: {text!r}')
    operation, value, next_port = match.groups()
    value = Decimal(value)
    if operation.lower() == 'add': total += value
    elif operation.lower() == 'minus': total -= value
    elif operation.lower() == 'multiply': total *= value
    elif operation.lower() == 'divide': total /= value
    print(f'{port}: {operation} {value} -> {total}')
    port = int(next_port)
print(f'Final answer: {total:.2f}')
