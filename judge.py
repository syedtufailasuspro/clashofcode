import requests
from pathlib import Path

solution = Path("solution.py")
base = Path("tests/case1")

with open(solution) as f:
    code = f.read()

with open(base.with_suffix(".in")) as f:
    inp = f.read()

with open(base.with_suffix(".out")) as f:
    expected = f.read().strip()

response = requests.post("https://emkc.org/api/v2/piston/execute", json={
    "language": "python",
    "version": "3.10.0",
    "files": [{"content": code}],
    "stdin": inp
})


result = response.json()
print(result)
output = result["run"]["stdout"].strip()

if output != expected:
    print("WA on one or more testcases")
else:
    print("ACCEPTED")
 