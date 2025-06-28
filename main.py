import argparse
import json
import os
import csv
from core.scanner import scan_username
import asyncio

PLATFORMS_PATH = os.path.join(os.path.dirname(__file__), 'core', 'platforms.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output', 'reports')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def export_results(results, username, fmt):
    out_path = os.path.join(OUTPUT_DIR, f"{username}_results.{fmt}")
    found = [r for r in results if r[2]]
    if fmt == "json":
        with open(out_path, "w") as f:
            json.dump([
                {"platform": p, "url": u, "score": s, "metadata": m} for p, u, found, s, m in found
            ], f, indent=2)
    elif fmt == "csv":
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["platform", "url", "score", "metadata"])
            for p, u, found, s, m in found:
                writer.writerow([p, u, s, m])
    elif fmt == "txt":
        with open(out_path, "w") as f:
            for p, u, found, s, m in found:
                f.write(f"{p}: {u} (score: {s})\n")
    print(f"Results exported to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Social Media Username Tracker (OSINT Tool)")
    parser.add_argument("username", help="Username to scan")
    parser.add_argument("--output", choices=["json", "csv", "txt"], help="Export results to file")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode (random user-agent)")
    parser.add_argument("--proxy", help="Proxy URL (e.g., socks5://127.0.0.1:9050)")
    args = parser.parse_args()

    with open(PLATFORMS_PATH, "r") as f:
        platforms = json.load(f)
    results = asyncio.run(scan_username(args.username, platforms, stealth=args.stealth, proxy=args.proxy))
    if args.output:
        export_results(results, args.username, args.output)

if __name__ == "__main__":
    main() 