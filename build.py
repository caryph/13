from pathlib import Path
from shutil import rmtree
import yaml

_DIR_IN = "content"
_DIR_OUT = "public"

root = Path(_DIR_IN)
output = Path(_DIR_OUT)

class BuildError(Exception):
    pass

def process_file(p: Path):
    content = p.read_text(encoding="utf-8")
    try:
        _, header, body = content.split("---\n", 2)
    except ValueError:
        if content.endswith("---"): raise BuildError(f"{p}: content is empty")
        else: raise BuildError(f"{p}: file header broken")
    
    meta: dict = yaml.safe_load(header)
    if 'path' not in meta and p.name == "index.md":
        meta['path'] = "index"
    
    try:
        path = Path(meta['path'])
    except KeyError:
        raise BuildError(f"{p}: must specify 'path' in header")

    public_path = Path(f"{output}/{path}.html")
    public_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.write_text(body.lstrip())



if output.exists():
    rmtree(output)

for p in root.rglob("*"):
    if p.is_symlink() or p.is_dir():
        continue
    process_file(p)