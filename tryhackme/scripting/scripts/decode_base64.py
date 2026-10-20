import argparse
import base64
from pathlib import Path

parser = argparse.ArgumentParser(description='Decode the Scripting room file 50 times')
parser.add_argument('file', type=Path)
args = parser.parse_args()
data = args.file.read_bytes()
for _ in range(50):
    data = base64.b64decode(data)
print(data.decode('utf-8'))
