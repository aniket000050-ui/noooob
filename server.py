#!/usr/bin/python
import os, sys, json, time, threading
from flask import Flask, request, jsonify

app = Flask(__name__)
bomb_thread = None
bomb_running = False
stop_flag = False

def run_bomber(cc, target, mode, count, delay, threads, loop):
    global bomb_running, stop_flag
    bomb_running = True
    stop_flag = False
    try:
        from auto_bomber import auto_bomb
        auto_bomb(cc, target, mode, count, delay, threads, loop)
    except Exception as e:
        print(f"Bomber error: {e}")
    finally:
        bomb_running = False

@app.route("/")
def home():
    return jsonify({"status": "running" if bomb_running else "idle", "endpoints": ["/start", "/stop", "/status"]})

@app.route("/start", methods=["POST"])
def start():
    global bomb_thread
    if bomb_running:
        return jsonify({"error": "Already running"}), 400
    data = request.json or {}
    cc = data.get("cc", os.environ.get("TARGET_CC", "91"))
    target = data.get("target", os.environ.get("TARGET_NUM", ""))
    mode = data.get("mode", os.environ.get("BOMB_MODE", "sms"))
    count = int(data.get("count", os.environ.get("BOMB_COUNT", "50")))
    delay = float(data.get("delay", os.environ.get("BOMB_DELAY", "1")))
    threads = int(data.get("threads", os.environ.get("BOMB_THREADS", "5")))
    loop = data.get("loop", os.environ.get("BOMB_LOOP", "false")).lower() == "true"

    if not target:
        return jsonify({"error": "No target number configured. Set TARGET_NUM env or pass in body."}), 400

    bomb_thread = threading.Thread(target=run_bomber, args=(cc, target, mode, count, delay, threads, loop), daemon=True)
    bomb_thread.start()
    return jsonify({"message": f"Bombing started on +{cc} {target} ({mode})"})

@app.route("/stop", methods=["POST"])
def stop():
    global bomb_running, stop_flag
    stop_flag = True
    bomb_running = False
    return jsonify({"message": "Stopping bomber..."})

@app.route("/status")
def status():
    return jsonify({"running": bomb_running})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
