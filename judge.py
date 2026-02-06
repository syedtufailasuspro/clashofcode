import requests
from pathlib import Path

solution = Path("main.cpp")
base = Path("tests/case1")

with open(solution) as f:
    code = f.read()

with open(base.with_suffix(".in")) as f:
    inp = f.read()

with open(base.with_suffix(".out")) as f:
    expected = f.read().strip()

import requests
from pathlib import Path

# ... (your file loading logic remains the same) ...

payload = {
    "language": "cpp",
    "version": "*", # Using '*' is safer than hardcoding a version
    "files": [{"name": "main.cpp", "content": code}],
    "stdin": inp
}

response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
result = response.json()

# 1. Check if the API returned an error message (e.g., unsupported language)
if "message" in result:
    print(f"API Error: {result['message']}")
    exit()

# 2. Check for Compilation Errors
if "compile" in result and result["compile"]["stderr"]:
    print("COMPILATION ERROR:")
    print(result["compile"]["stderr"])
    exit()

# 3. Safely check for Runtime Errors or Output
if "run" in result:
    run_info = result["run"]
    
    if run_info["stderr"]:
        print("RUNTIME ERROR / STDERR:")
        print(run_info["stderr"])
    
    output = run_info["stdout"].strip()
    
    if output != expected:
        print(f"WA: Expected '{expected}', but got '{output}'")
    else:
        print("ACCEPTED")
else:
    print("Unknown error occurred:", result)