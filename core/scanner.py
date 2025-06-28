import aiohttp
import asyncio
from fake_useragent import UserAgent
from colorama import Fore, Style
from tqdm import tqdm
import os
import json

PLATFORMS_PATH = os.path.join(os.path.dirname(__file__), 'platforms.json')

async def fetch(session, url, platform, stealth_headers):
    try:
        async with session.get(url, headers=stealth_headers, timeout=10) as resp:
            if resp.status == 200:
                # Placeholder for metadata extraction
                metadata = None
                return platform, url, True, metadata
            else:
                return platform, url, False, None
    except Exception:
        return platform, url, False, None

async def scan_username(username, platforms, stealth=True, proxy=None):
    ua = UserAgent()
    stealth_headers = {"User-Agent": ua.random} if stealth else {}
    results = []
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for platform, info in platforms.items():
            url = info["url"].format(username)
            tasks.append(fetch(session, url, platform, stealth_headers))
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scanning"):
            platform, url, found, metadata = await f
            results.append((platform, url, found, metadata))
            if found:
                print(f"{Fore.GREEN}✓ Found{Style.RESET_ALL} {platform}: {url}")
            else:
                print(f"{Fore.RED}✗ Not Found{Style.RESET_ALL} {platform}")
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    with open(PLATFORMS_PATH, "r") as f:
        platforms = json.load(f)
    asyncio.run(scan_username(username, platforms)) 