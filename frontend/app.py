import os
import requests
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

API_URL = os.getenv("API_URL", "http://api:8080")
app = FastAPI()


def get_nodes():
    try:
        return requests.get(f"{API_URL}/api/nodes", timeout=3).json()
    except Exception:
        return []


def get_health():
    try:
        return requests.get(f"{API_URL}/health", timeout=3).json()
    except Exception:
        return {"status": "error", "db": "unknown", "nodes_count": 0}


def render(nodes, health, msg=""):
    rows = "".join(
        f"<tr><td>{n['name']}</td><td>{n['host']}</td><td>{n['port']}</td><td>{n['status']}</td></tr>"
        for n in nodes
    ) or "<tr><td colspan='4'>No nodes registered yet.</td></tr>"

    color = "green" if health.get("status") == "ok" else "red"
    msg_html = f'<p style="color:green">{msg}</p>' if msg else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Node Registry nodes</title>
</head>
<body>
  <h1>Node Registry Dashboard</h1>
  <p style="color:{color}">
    API: {health.get("status","?")} | DB: {health.get("db","?")} | Active nodes: {health.get("nodes_count",0)}
  </p>
  {msg_html}

  <h2>Registered Nodes</h2>
  <table border="1" cellpadding="6">
    <tr><th>Name</th><th>Host</th><th>Port</th><th>Status</th></tr>
    {rows}
  </table>

  <h2>Register Node</h2>
  <form method="post" action="/register">
    <label>Name: <input name="name" required></label><br><br>
    <label>Host: <input name="host" required></label><br><br>
    <label>Port: <input name="port" type="number" value="8080" min="1" max="65535" required></label><br><br>
    <button type="submit">Register</button>
  </form>

  <h2>Delete Node</h2>
  <form method="post" action="/delete">
    <label>Name: <input name="name" required></label><br><br>
    <button type="submit">Delete</button>
  </form>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=render(get_nodes(), get_health()))


@app.post("/register")
def register(name: str = Form(...), host: str = Form(...), port: int = Form(...)):
    try:
        requests.post(f"{API_URL}/api/nodes", json={"name": name, "host": host, "port": port}, timeout=3)
    except Exception:
        pass
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete")
def delete_node(name: str = Form(...)):
    try:
        requests.delete(f"{API_URL}/api/nodes/{name}", timeout=3)
    except Exception:
        pass
    return RedirectResponse(url="/", status_code=303)
