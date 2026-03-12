from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from services.android_enterprise import AndroidEnterpriseManager


app = Flask(__name__)
manager = AndroidEnterpriseManager()


@app.get("/")
def index():
    return render_template(
        "index.html",
        summary=manager.summary(),
        actions=manager.available_actions(),
        devices=manager.devices(),
        policies=manager.policies(),
        activity=manager.activity(),
    )


@app.get("/api/dashboard")
def dashboard():
    return jsonify(
        {
            "summary": manager.summary(),
            "devices": manager.devices(),
            "policies": manager.policies(),
            "activity": manager.activity(),
        }
    )


@app.post("/api/actions/<action_name>")
def run_action(action_name: str):
    payload = request.get_json(silent=True) or {}
    result = manager.run_action(action_name, payload)
    return jsonify(result), (200 if result["ok"] else 400)


if __name__ == "__main__":
    app.run(debug=True)
