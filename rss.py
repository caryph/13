from datetime import datetime, timezone, time, timedelta
from common import _DIR_OUT, _DOMAIN, _AUTHOR, _DATE_FORMAT, _TIMEZONE
from html import escape
from wall import excerpt

_BASE_URL = "https://" + _DOMAIN

def get_time(d: str | None = None):
    if d is None:
        dt = datetime.now(timezone.utc)
    else:
        dt = datetime.strptime(d, _DATE_FORMAT).replace(tzinfo=timezone(timedelta(hours=_TIMEZONE)))
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def format_entry(meta: dict):
    url = f"{_BASE_URL}/{meta['path']}"
    title = meta['title'] if meta.get('title') else excerpt(meta['_html'], 40)[0]
    return f"""<entry>
        <title>{escape(str(title))}</title>
        <link href="{url}/"/>
        <id>{url}</id>
        <updated>{get_time(meta['date'])}</updated>
        <content type="html" xml:base="{url}/">{escape(meta['_html'])}</content>
    </entry>
    """

def build_feed(entries: list, title: str, id: str):
    entries_xml = "\n".join(format_entry(meta) for meta in entries)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>{title}</title>
    <id>{id}</id>
    <link href="{_BASE_URL}/"/>
    <updated>{get_time()}</updated>
    <author>
        <name>{_AUTHOR}</name>
        <uri>{_BASE_URL}/</uri>
    </author>
    {entries_xml}
</feed>
"""

def update_feeds(wall: list):
    with open(_DIR_OUT + "/feed.xml", "w", encoding="utf-8") as f:
        entries = (meta for meta in wall if meta.get('title'))
        f.write(build_feed(entries, '13m', _BASE_URL))

    with open(_DIR_OUT + "/everything.xml", "w", encoding="utf-8") as f:
        f.write(build_feed(wall, '13m (everything)', f"{_BASE_URL}/everything.xml"))