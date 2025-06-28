import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import json
import asyncio
from core.scanner import scan_username

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))
PLATFORMS_PATH = os.path.join(BASE_DIR, 'core', 'platforms.json')
EXPORT_DIR = os.path.join(BASE_DIR, 'output', 'reports')
os.makedirs(EXPORT_DIR, exist_ok=True)

scan_cache = {}

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "results": None, "username": None})

@app.post('/scan', response_class=HTMLResponse)
async def scan(request: Request, username: str = Form(...)):
    with open(PLATFORMS_PATH, 'r') as f:
        platforms = json.load(f)
    results = await scan_username(username, platforms, stealth=True)
    scan_cache[username] = results
    return templates.TemplateResponse('index.html', {"request": request, "results": results, "username": username})

@app.post('/export', response_class=FileResponse)
async def export(request: Request, username: str = Form(...), format: str = Form(...)):
    results = scan_cache.get(username)
    if not results:
        return HTMLResponse("No results to export.", status_code=400)
    out_path = os.path.join(EXPORT_DIR, f"{username}_results.{format}")
    found = [r for r in results if r[2]]
    if format == "json":
        with open(out_path, "w") as f:
            json.dump([
                {"platform": p, "url": u, "metadata": m} for p, u, found, m in found
            ], f, indent=2)
    elif format == "csv":
        import csv
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["platform", "url", "metadata"])
            for p, u, found, m in found:
                writer.writerow([p, u, m])
    elif format == "txt":
        with open(out_path, "w") as f:
            for p, u, found, m in found:
                f.write(f"{p}: {u}\n")
    return FileResponse(out_path, filename=os.path.basename(out_path)) 