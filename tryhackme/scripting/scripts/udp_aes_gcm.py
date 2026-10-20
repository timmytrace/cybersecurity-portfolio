import argparse
import hashlib
import re
import socket
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

parser = argparse.ArgumentParser(description='Decrypt candidates from the authorized UDP lab')
parser.add_argument('host', help='Current TryHackMe task machine IP')
args = parser.parse_args()
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.settimeout(10)
    sock.connect((args.host, 4000))
    def exchange(payload):
        sock.send(payload)
        return sock.recv(65535)
    print(exchange(b'hello').decode('utf-8', errors='replace'))
    info = exchange(b'ready')
    key = re.search(rb'key:(\S+)', info).group(1)
    nonce = re.search(rb'iv:(\S+)', info).group(1)
    start = info.index(b'SHA256 checksum of ') + len(b'SHA256 checksum of ')
    expected = info[start:start + 32]
    if len(expected) != 32:
        raise SystemExit('Incomplete SHA256 digest')
    aes = AESGCM(key)
    sock.send(b'final')
    checked = 0
    while True:
        try:
            ciphertext = sock.recv(65535)
            tag = sock.recv(65535)
        except socket.timeout:
            raise SystemExit(f'Timed out after {checked} candidates. Restart the handshake and retry.')
        if len(tag) != 16:
            raise SystemExit('Unexpected tag length; packet pairing may be lost. Restart and retry.')
        try:
            plaintext = aes.decrypt(nonce, ciphertext + tag, None)
        except InvalidTag:
            raise SystemExit('Authentication failed. Possible packet loss/reordering; restart and retry.')
        checked += 1
        if hashlib.sha256(plaintext).digest() == expected:
            print('FLAG:', plaintext.decode('utf-8'))
            break
        print('Checked candidate', checked)
