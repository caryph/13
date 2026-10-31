from datetime import datetime, timezone, time, timedelta
from common import _DIR_OUT, _DOMAIN, _AUTHOR, _DATE_FORMAT, _TIMEZONE
from html import escape

_BASE_URL = "https://" + _DOMAIN

def get_time(d: str | None = None):
    if d is None:
        dt = datetime.now(timezone.utc)
    else:
        dt = datetime.strptime(d, _DATE_FORMAT).replace(tzinfo=timezone(timedelta(hours=_TIMEZONE)))
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def format_entry(meta: dict):
    url = f"{_BASE_URL}/{meta['path']}"
    return f"""<entry>
        <title>{escape(str(meta['title']))}</title>
        <link href="{url}/"/>
        <id>{url}</id>
        <updated>{get_time(meta['date'])}</updated>
        <content type="html" xml:base="{url}/">{escape(meta['_html'])}</content>
    </entry>
    """

def get_feed(notes: list):
    entries = "\n".join(format_entry(meta) for meta in notes if meta.get('title'))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>13m</title>
    <link href="{_BASE_URL}/"/>
    <updated>{get_time()}</updated>
    <author>
        <name>{_AUTHOR}</name>
        <uri>{_BASE_URL}/</uri>
    </author>
    <id>{_BASE_URL}</id>
    {entries}
</feed>
"""

def update_feed(notes: list):
    with open(_DIR_OUT + "/feed.xml", "w", encoding="utf-8") as f:
        f.write(get_feed(notes))