from pathlib import Path
from datetime import datetime
from html import unescape
import re

from common import BuildError, _DIR_IN, _DATE_FORMAT

root = Path(_DIR_IN)

def is_on_wall(p: Path):
    parts = p.relative_to(root).parts
    return len(parts) > 1 and parts[0] == "wall"


def excerpt(html: str, limit=130) -> tuple[str, int]:
    text = " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())
    if len(text) <= limit:
        return text, 0
    short = text[:limit].rsplit(" ", 1)[0]
    return short + "…", len(text.split()) - len(short.split())


def preprocess_wall_post(p: Path, meta: dict):
    d = str(meta.get("date", ""))
    try:
        ok = datetime.strptime(d, _DATE_FORMAT).strftime(_DATE_FORMAT) == d
    except ValueError: ok = False
    if not ok: raise BuildError(f"{p}: 'date' must adhere to the format: {_DATE_FORMAT}")

    if meta.get("title") and "path" not in meta:
        raise BuildError(f"{p}: titled posts require a specified 'path'")
    elif not meta.get("title"):
        if "path" in meta:
            raise BuildError(f"{p}: untitled posts get their url automatically - remove 'path'")
        meta['path'] = d.replace("@", "/").replace(":", "")

    meta['day'] = d.split("@")[0]
    meta.setdefault('template', 'post' if meta.get('title') else 'note')


def generate_wall(log: list):
    rows = []
    for meta in log:
        date, time = meta["date"].split("@")
        if meta.get('title'):
            content = f'<a href="/{meta["path"]}/">{meta["title"]}</a>'
        else:
            short, rest = excerpt(meta['_html'])
            url_symbol = f"+{rest}" if rest > 0 else "↗"
            content = f'@{time} {short} <a href="/{meta["path"]}/">{url_symbol}</a>'
        
        rows.append(f'<li><time class="muted">{date}</time> <span>{content}</span></li>')
    return f'<ul class="note-list">{"\n".join(rows)}</ul>'