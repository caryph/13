from pathlib import Path
from shutil import rmtree, copytree
import yaml
import markdown

from common import _DIR_IN, _DIR_OUT, _DIR_STATIC, _DIR_TEMPLATES, _TEMPLATES
from rss import update_feed

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

def write_page(path: str, html: str, meta: dict):
    html = read_template("base").replace("%content%", html)
    for k, v in meta.items():
        html = html.replace(f"%{k}%", str(v))

    out = output / "index.html" if path == "index" else output / path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return meta
    
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
    meta['_html'] = html
    template = meta.get('template') or fetch_template(p)
    if template:
        html = read_template(template).replace("%content%", html)

    if "path" not in meta:
        raise BuildError(f"{p}: must specify 'path' in header")
    
    return write_page(str(meta["path"]), html, meta)

def generate_note_list(notes: list):
    rows = "\n".join(f'<li><time class="muted">{n["date"]}</time> <a href="/{n['path']}/">{n['title']}</a></li>' for n in notes)
    return f'<ul class="note-list">{rows}</ul>'


if output.exists():
    rmtree(output)

copytree(_DIR_STATIC, output, dirs_exist_ok=True)

def is_note(p: Path):
    parts = p.relative_to(root).parts
    return len(parts) > 1 and parts[0] == "n"

notes = []
for p in root.rglob("*.md"):
    if p.is_symlink() or p.is_dir():
        continue
    entry = process_file(p)
    if is_note(p):
        if "date" not in entry:
            raise BuildError(f"{p}: 'date' header missing")
        notes.append(entry)

    notes.sort(key=lambda n: n["date"], reverse=True)
    write_page("n", generate_note_list(notes), {"title": "notes"})
    update_feed(notes)