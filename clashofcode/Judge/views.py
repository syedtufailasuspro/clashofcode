from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from battle.models import Battle
import requests
from django.http import HttpResponse, JsonResponse
# Create your views here.


@login_required(login_url='login')
def submit_code(request):
    data = json.loads(request.body)
    #battle_id, code, language, problem, user
    battle_id = data["battle_id"]
    battle = Battle.objects.filter(id=battle_id).first()
    language = data["language"]
    version = data["version"]
    problem = battle.problem
    code = data["code"]


    for sample in problem.samples:
        inp = sample['input']
        expected = sample['output']

        response = requests.post("https://emkc.org/api/v2/piston/execute", json={
        "language": language,
        "version": version,
        "files": [{"content": code}],
        "stdin": inp
        })

        result = response.json()

        print(result)
    
    return JsonResponse({'status':200})


@login_required(login_url='login')
def run_code(request):
    data = json.loads(request.body)
    #battle_id, code, language, problem, user
    battle_id = data["battle_id"]
    battle = Battle.objects.filter(id=battle_id).first()
    language = data["language"]
    version = data["version"]
    problem = battle.problem
    code = data["code"]
    inp = data["input"]

    if not inp:
        return JsonResponse({"status":400, "message":"Missing Input"})

    response = requests.post("https://emkc.org/api/v2/piston/execute", json={
        "language": language,
        "version": version,
        "files": [{"content": code}],
        "stdin": inp
        })

    result = response.json()

    print(result)
    
    return JsonResponse({'status':200})