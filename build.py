from pathlib import Path
from shutil import rmtree, copytree
import yaml
import markdown

_TEMPLATES = {
    "notes": "post.html"
}

_DIR_IN = "content"
_DIR_OUT = "public"
_DIR_STATIC = "static"
_DIR_TEMPLATES = "templates"

root = Path(_DIR_IN)
output = Path(_DIR_OUT)

class BuildError(Exception):
    pass

def fetch_template(p: Path):
    parent_dirs = p.relative_to(root).parts
    for parent in reversed(parent_dirs):
        if parent in _TEMPLATES:
            return _TEMPLATES[parent]
    return None

def read_template(name: str):
    if not name.endswith(".html"):
        name += ".html"
    try:
        return Path(_DIR_TEMPLATES, name).read_text()
    except FileNotFoundError:
        raise BuildError(f"{p}: template '{name}' file missing")
    

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

    html = markdown.markdown(body)
    template = meta.get('template') or fetch_template(p)
    if template:
        html = read_template(template).replace("%content%", html)
    html = read_template("base").replace("%content%", html)
    for k, v in meta.items():
        html = html.replace(f"%{k}%", str(v))

    try:
        path = Path(meta['path'])
    except KeyError:
        raise BuildError(f"{p}: must specify 'path' in header")

    public_path = Path(output, f"{path}.html")
    public_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.write_text(html)
    return meta



if output.exists():
    rmtree(output)

copytree(_DIR_STATIC, output, dirs_exist_ok=True)

for p in root.rglob("*.md"):
    if p.is_symlink() or p.is_dir():
        continue
    entry = process_file(p)