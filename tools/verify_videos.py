#!/usr/bin/env python3
"""Usage: python3 tools/verify_videos.py ID [ID ...]
Checks each YouTube id: oEmbed title + channel, embeddable (via the youtube-nocookie embed
page with a Referer), and duration in seconds. Results are saved to tools/verified.json."""
import sys, json, re, urllib.request, urllib.parse, pathlib
P = pathlib.Path(__file__).with_name('verified.json')
db = json.loads(P.read_text()) if P.exists() else {}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def get(url, ref=None):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en"}
    if ref: h["Referer"] = ref
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20) as r:
        return r.read().decode('utf-8', 'replace')
for vid in sys.argv[1:]:
    rec = {"id": vid}
    try:
        o = json.loads(get("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}")))
        rec["title"], rec["channel"] = o["title"], o["author_name"]
    except Exception as e:
        rec["oembed_error"] = str(e)
    try:
        s = get(f"https://www.youtube-nocookie.com/embed/{vid}?hl=en", ref="https://grrhero.github.io/")
        m = re.search(r'"embedded_player_response":"((?:[^"\\]|\\.)*)"', s)
        r = json.loads(json.loads('"' + m.group(1) + '"'))
        ps = r.get("previewPlayabilityStatus", {})
        rec["status"] = ps.get("status"); rec["embeddable"] = bool(ps.get("playableInEmbed")) and ps.get("status") == "OK"
        d = re.search(r'"videoDurationSeconds":\s*"(\d+)"', json.dumps(r))
        rec["seconds"] = int(d.group(1)) if d else None
        if ps.get("reason"): rec["reason"] = ps["reason"]
    except Exception as e:
        rec["embed_error"] = str(e)
    db[vid] = rec
    sec = rec.get("seconds")
    print(f"{vid} | {rec.get('channel')} | {rec.get('title')} | {sec and f'{sec//60}:{sec%60:02d}'} | embed={rec.get('embeddable')} {rec.get('reason','')}{rec.get('oembed_error','')}")
P.write_text(json.dumps(db, indent=1, ensure_ascii=False))
