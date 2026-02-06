from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from battle.models import Battle
import requests
from django.http import HttpResponse, JsonResponse
# Create your views here.

LANG_FILE_MAP = {
    "python": "main.py",
    "py": "main.py",

    "cpp": "main.cpp",
    "c++": "main.cpp",

    "c": "main.c",

    "java": "Main.java",

    "go": "main.go",

    "javascript": "main.js",
    "js": "main.js",
}


@login_required(login_url='login')
def submit_code(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "BAD_REQUEST", "message": "Invalid JSON body"}, status=400)

    #battle_id, code, language, problem, user
    battle_id = data.get("battle_id")
    language = data.get("language")
    version = data.get("version")
    code = data.get("code")

    if not battle_id or not language or not code:
        return JsonResponse({"status": "BAD_REQUEST", "message": "Missing required fields"}, status=400)

    battle = Battle.objects.filter(id=battle_id).first()
    if not battle:
        return JsonResponse({"status": "NOT_FOUND", "message": "Battle not found"}, status=404)

    if language not in LANG_FILE_MAP:
        return JsonResponse({"status": "BAD_REQUEST", "message": "Unsupported language"}, status=400)

    problem = battle.problem

    count = 1
    for sample in problem.samples:
        inp = sample['input']
        expected = sample['output']

        filename = LANG_FILE_MAP[language]

        response = requests.post("https://emkc.org/api/v2/piston/execute", json={
            "language": language,
            "version": '*',
            "files": [{
                "name": filename,
                "content": code
            }],
            "stdin": inp
        })

        result = response.json()
        print(result)

        compile_error = result.get("compile", {}).get("stderr", "").strip()
        if compile_error:
            return JsonResponse({
                "status": "CE",
                "message": f"Compilation Error on testcase {count}",
                "output": compile_error
            })

        runtime_error = result.get("run", {}).get("stderr", "").strip()
        if runtime_error:
            return JsonResponse({
                "status": "RE",
                "message": f"Runtime Error on testcase {count}",
                "output": runtime_error
            })
        
        output = result.get("run", {}).get("stdout", "").strip()
        if expected != output:
            return JsonResponse({
                "status": "WA",
                "message": f"Wrong Answer on testcase {count}",
                "output": output
            })
        
        count += 1
    
    return JsonResponse({'status':"AC"})


@login_required(login_url='login')
def run_code(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON body"}, status=400)

    #battle_id, code, language, problem, user
    battle_id = data.get("battle_id")
    language = data.get("language")
    version = data.get("version")
    code = data.get("code")
    inp = data.get("input")

    if not battle_id or not language or not code:
        return JsonResponse({"status": 400, "message": "Missing required fields"}, status=400)

    if not inp:
        return JsonResponse({"status": 400, "message": "Missing Input"}, status=400)

    battle = Battle.objects.filter(id=battle_id).first()
    if not battle:
        return JsonResponse({"status": 404, "message": "Battle not found"}, status=404)

    if language not in LANG_FILE_MAP:
        return JsonResponse({"status": 400, "message": "Unsupported language"}, status=400)

    filename = LANG_FILE_MAP[language]

    response = requests.post("https://emkc.org/api/v2/piston/execute", json={
        "language": language,
        "version": '*',
        "files": [{
            "name": filename,
            "content": code
        }],
        "stdin": inp
    })

    result = response.json()
    print(result)

    compile_error = result.get("compile", {}).get("stderr", "").strip()
    if compile_error:
        return JsonResponse({"status": 400, "output": compile_error})

    runtime_error = result.get("run", {}).get("stderr", "").strip()
    if runtime_error:
        return JsonResponse({"status": 400, "output": runtime_error})

    output = result.get("run", {}).get("stdout", "").strip()

    return JsonResponse({"status": 200, "output": output})