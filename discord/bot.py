import json
import sys
import yaml
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from pathlib import Path

sys.path.append("..")
from common import _DOMAIN

_SITE = "https://" + _DOMAIN
_ATOM = "{http://www.w3.org/2005/Atom}"
_TOKEN = Path("secret.txt").read_text().strip()

config = yaml.safe_load(Path("config.yml").read_text())
sent = Path("sent.txt")

def read_feed(name: str):
    with urlopen(f"{_SITE}/{name}", timeout=10) as response:
        root = ElementTree.fromstring(response.read())
    entries = root.findall(_ATOM + "entry")
    return {e.find(_ATOM + "link").get("href"): e.find(_ATOM + "title").text for e in entries}

def send(path: str, body: dict):
    request = Request(
        f"https://discord.com/api/v10/channels/{config['channel_id']}/{path}",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": "Bot " + _TOKEN,
            "Content-Type": "application/json",
            "User-Agent": f"DiscordBot ({_SITE}, 1.0)"
        }
    )
    with urlopen(request, timeout=10) as response:
        return json.load(response)


articles = read_feed("feed.xml")
everything = read_feed("everything.xml")

if not sent.exists():
    sent.write_text("\n".join(everything) + "\n")

sent_urls = sent.read_text().split()

for url, title in reversed(everything.items()):
    if url in sent_urls:
        continue
    ping = "@everyone" if url in articles else f"<@&{config['notes_role_id']}>"
    if "--post" not in sys.argv:
        print("would send:", ping, url)
        continue

    msg = send("messages", {"content": f"{ping} {url}"})

    with sent.open("a") as f:
        f.write(url + "\n")
    send(f"messages/{msg['id']}/threads", {"name": title[:100]})