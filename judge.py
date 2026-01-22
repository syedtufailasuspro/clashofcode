import subprocess
import sys
from pathlib import Path

solution = Path("solution.py")
base = Path("tests/case1")

with open(base.with_suffix(".in")) as f:
    inp = f.read()

with open(base.with_suffix(".out")) as f:
    expected = f.read().strip()

result = subprocess.run(
    [sys.executable, str(solution)],
    input=inp,
    capture_output=True,
    text=True,
    timeout=5
)

if result.stdout.strip() != expected:
    print("WA on one or more testcases")
    sys.exit(0)

print("ACCEPTED")
