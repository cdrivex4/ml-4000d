import urllib.request
import json

def get_tree(repo, sha='dev'):
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

paths_simp = get_tree("reticulatedpines/magiclantern_simplified", "dev")
print("magiclantern_simplified paths count:", len(paths_simp))
matching = [p for p in paths_simp if any(k in p.lower() for k in ['dumper', 'pack-fir', '1300d', '4000d', 't100', 'contrib/qemu'])]
print("Matching paths in simplified dev:")
for p in matching[:40]:
    print("  ", p)
