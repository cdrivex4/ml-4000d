import urllib.request
import json

def get_tree(repo, sha='master'):
    url = f"https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [x['path'] for x in data.get('tree', [])]
    except Exception as e:
        print(f"Error {repo}:", e)
        return []

paths_hg = get_tree("reticulatedpines/magiclantern_hg_02")
print("magiclantern_hg_02 paths count:", len(paths_hg))
dumper_paths = [p for p in paths_hg if any(k in p.lower() for k in ['dumper', 'pack-fir', 'fir', '1300d', '4000d', 't100'])]
print("Matching paths in hg_02:")
for p in dumper_paths[:40]:
    print("  ", p)
