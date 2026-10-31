import urllib.request
import re
import sys

def check_url(target_url):
    archive_url = f"https://archive.ph/{target_url}"
    print(f"Checking {archive_url} ...")
    req = urllib.request.Request(archive_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode('utf-8', errors='ignore')
            print(f"Fetched {len(html)} chars")
            # find all snapshot links
            matches = re.findall(r'href=[\'"](https?://archive\.[a-z]+/[a-zA-Z0-9]+)[\'"]', html)
            print("Snapshots found:", set(matches))
            # Also search for dates and links
            for m in re.finditer(r'<a\s+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', html, re.DOTALL):
                href, text = m.group(1), m.group(2).strip()
                if any(x in href for x in ['archive.', target_url, 'magiclantern']):
                    print(f"Link: {href} -> {text[:60]}")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    for url in [
        'https://a1ex.magiclantern.fm/debug/portable-rom-dumper/new/DMP4000D.FIR',
        'https://www.magiclantern.fm/forum/index.php?topic=16534.0',
        'https://www.magiclantern.fm/forum/index.php?topic=17969.0',
        'https://www.magiclantern.fm/forum/index.php?topic=19417.0',
        'https://www.magiclantern.fm/forum/index.php?topic=23369.0',
    ]:
        check_url(url)
