from pathlib import Path
from shutil import rmtree, copytree
import yaml
import markdown

from common import BuildError, _DIR_IN, _DIR_OUT, _DIR_STATIC, _DIR_TEMPLATES
from wall import is_on_wall, preprocess_wall_post, generate_wall, excerpt
from rss import update_feed

root = Path(_DIR_IN)
output = Path(_DIR_OUT)

def read_template(name: str):
    if not name.endswith(".html"):
        name += ".html"
    try:
        return Path(_DIR_TEMPLATES, name).read_text()
    except FileNotFoundError:
        raise BuildError(f"template '{name}' file missing")

_written = {}

def write_page(path: str, html: str, meta: dict, src: str | None = None):
    html = read_template("base").replace("%content%", html)
    for k, v in meta.items():
        html = html.replace(f"%{k}%", str(v))

    out = output / "index.html" if path == "index" else output / path / "index.html"

    if src:
        if out in _written:
            raise BuildError(f"{src}: path /{path} is already taken by {_written[out]}")
        _written[out] = src

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
        

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
    
    if is_on_wall(p):
        preprocess_wall_post(p, meta)

    html = markdown.markdown(body, extensions=["tables"])
    meta['_html'] = html

    template = meta.get('template')
    if template:
        html = read_template(template).replace("%content%", html)

    if "path" not in meta:
        raise BuildError(f"{p}: must specify 'path' in header")

    page = dict(meta)
    if not page.get('title'):
        page['title'] = excerpt(meta['_html'])[0]
    
    write_page(str(meta["path"]), html, page, p)
    return meta

if output.exists():
    rmtree(output)

copytree(_DIR_STATIC, output, dirs_exist_ok=True)

wall = []
for p in root.rglob("*.md"):
    if p.is_symlink() or p.is_dir():
        continue
    meta = process_file(p)
    if is_on_wall(p):
        wall.append(meta)

wall.sort(key=lambda n: n["date"], reverse=True)
write_page("w", generate_wall(wall), {"title": "wall"}, "wall page")
update_feed(wall)