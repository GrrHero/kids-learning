#!/usr/bin/env python3
"""Regenerate index.html from lineup.json (data is inlined so the page is one file).
Usage: python3 build.py
See README-lineup.md for the data format.
"""
import datetime as dt, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEG_KEYS = ["amTogether", "amYounger", "pmOlder", "pmTogether"]
# Soft limits (minutes) per segment; build warns, never fails, when a segment runs long/short.
SEG_RANGE = {"amTogether": (3, 7), "amYounger": (9, 16), "pmOlder": (9, 18), "pmTogether": (3, 9)}

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>Kids Learning</title>
<style>
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  html, body { margin: 0; min-height: 100%; }
  body {
    font-family: "Comic Sans MS", "Chalkboard SE", "Trebuchet MS", system-ui, sans-serif;
    background: linear-gradient(160deg, #ffe66d 0%, #ff9f68 45%, #a0e7e5 100%);
    background-attachment: fixed; color: #222; user-select: none;
  }
  button { font: inherit; touch-action: manipulation; cursor: pointer; }
  header { text-align: center; padding: 14px 16px 4px; }
  h1 { margin: 0; font-size: 46px; color: #fff; letter-spacing: 2px;
       text-shadow: 3px 3px 0 #ff5d8f, 6px 6px 0 rgba(0,0,0,.15); }
  .week { display: inline-block; margin-top: 6px; padding: 6px 22px; border-radius: 999px;
          background: #fff; font-size: 22px; font-weight: bold; color: #4b3fd6;
          box-shadow: 0 5px 0 rgba(0,0,0,.15); }
  nav { display: flex; align-items: center; justify-content: center; gap: 16px; padding: 14px 16px 4px; flex-wrap: wrap; }
  .navbtn { font-size: 30px; font-weight: bold; padding: 14px 30px; border-radius: 999px; border: none;
            color: #fff; background: #4b3fd6; box-shadow: 0 7px 0 #2e2494; min-width: 120px; }
  .navbtn:active { transform: translateY(5px); box-shadow: 0 2px 0 #2e2494; }
  .navbtn.alt { background: #2bb673; box-shadow: 0 7px 0 #1b7a4b; }
  .navbtn[disabled] { opacity: .35; }
  .day { text-align: center; }
  .dayname { font-size: 40px; font-weight: bold; color: #222; }
  .focus { font-size: 22px; color: #333; margin-top: 2px; }
  .today-pill { display: inline-block; margin-left: 10px; padding: 2px 14px; border-radius: 999px; background: #ff5d8f;
                color: #fff; font-size: 22px; vertical-align: middle; }
  main { padding: 10px 28px 40px; max-width: 1500px; margin: 0 auto; }
  section.seg { background: rgba(255,255,255,.55); border-radius: 30px; margin: 18px 0; padding: 14px 18px 20px;
                border: 6px solid var(--c); box-shadow: 0 8px 0 var(--c); }
  .seghead { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
  .icon { font-size: 46px; line-height: 1; }
  .seglabel { font-size: 36px; font-weight: bold; color: var(--c); text-shadow: 1px 1px 0 #fff; }
  .segmins { font-size: 22px; font-weight: bold; padding: 4px 16px; border-radius: 999px; background: var(--c); color: #fff; }
  .playall { margin-left: auto; font-size: 26px; font-weight: bold; padding: 10px 26px; border-radius: 999px; border: none;
             color: #fff; background: var(--c); box-shadow: 0 6px 0 rgba(0,0,0,.25); }
  .playall:active { transform: translateY(4px); box-shadow: 0 2px 0 rgba(0,0,0,.25); }
  .prompt { font-size: 21px; margin: 6px 4px 10px; color: #333; }
  .prompt b { color: var(--c); }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
  .card { display: flex; flex-direction: column; padding: 0; margin: 0; text-align: left; cursor: pointer;
          border-radius: 22px; overflow: hidden; background: #fff; color: inherit;
          box-shadow: 0 7px 0 var(--c), 0 12px 20px rgba(0,0,0,.15); border: 5px solid var(--c);
          transition: transform .12s; touch-action: manipulation; }
  .card:active { transform: scale(.96) translateY(5px); box-shadow: 0 3px 0 var(--c); }
  .thumb { position: relative; height: 0; padding-top: 56.25%; overflow: hidden; background: #ddd; flex: none; }
  .thumb img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
  .play { position: absolute; inset: 0; margin: auto; width: 76px; height: 76px; border-radius: 50%;
          background: rgba(255,255,255,.92); display: flex; align-items: center; justify-content: center;
          box-shadow: 0 4px 12px rgba(0,0,0,.3); }
  .play::after { content: ""; margin-left: 8px; border-style: solid; border-width: 18px 0 18px 30px;
                 border-color: transparent transparent transparent var(--c); }
  .dur { position: absolute; right: 8px; bottom: 8px; background: rgba(0,0,0,.78); color: #fff; font-size: 20px;
         font-weight: bold; padding: 2px 10px; border-radius: 8px; }
  .num { position: absolute; left: 8px; top: 8px; background: var(--c); color: #fff; font-size: 22px; font-weight: bold;
         width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
  .info { padding: 10px 14px 14px; }
  .title { font-size: 24px; font-weight: bold; line-height: 1.15; }
  .tag { display: inline-block; margin-top: 8px; padding: 3px 12px; border-radius: 999px; background: #eee;
         color: #444; font-size: 15px; font-family: system-ui, sans-serif; }
  .s-amTogether { --c: #f5a300; } .s-amYounger { --c: #2bb673; }
  .s-pmOlder { --c: #4b8bf5; } .s-pmTogether { --c: #c24bf5; } .s-weekend { --c: #ff5d8f; }
  /* week view */
  .weekgrid { display: grid; grid-template-columns: 210px repeat(5, 1fr); gap: 10px; }
  .wcell { background: #fff; border-radius: 16px; padding: 10px 12px; font-size: 17px; line-height: 1.2; }
  .wcell ul { margin: 0; padding-left: 18px; }
  .whead { background: #4b3fd6; color: #fff; font-size: 24px; font-weight: bold; text-align: center; border: none; }
  .whead.is-today { background: #ff5d8f; }
  .wseg { color: #fff; background: var(--c); font-size: 20px; font-weight: bold; display: flex; align-items: center; }
  #overlay { position: fixed; inset: 0; background: rgba(20,10,60,.94); display: none;
             flex-direction: column; align-items: center; justify-content: center; z-index: 10; padding: 20px; }
  #overlay.open { display: flex; }
  #back { position: absolute; top: 18px; left: 18px; font-size: 40px; font-weight: bold;
          padding: 14px 40px; border-radius: 999px; border: none; color: #fff;
          background: #ff5d8f; box-shadow: 0 8px 0 #c2185b; z-index: 2; }
  #back:active { transform: translateY(6px); box-shadow: 0 2px 0 #c2185b; }
  #nowplaying { position: absolute; top: 30px; right: 26px; left: 300px; text-align: right; color: #fff; font-size: 24px; }
  #playerWrap { width: min(92vw, calc((100vh - 150px) * 16 / 9)); height: min(calc(92vw * 9 / 16), calc(100vh - 150px)); margin-top: 80px;
                border-radius: 20px; overflow: hidden; background: #000; }
  #playerWrap iframe { width: 100%; height: 100%; border: 0; display: block; }
  .empty { background: #fff; border-radius: 24px; padding: 24px; font-size: 26px; text-align: center; }
</style>
</head>
<body>
<header>
  <h1>Kids Learning</h1>
  <div class="week" id="weektitle">__WEEK_HTML__</div>
</header>
<nav>
  <button class="navbtn" id="prev" type="button">&#9664; Prev</button>
  <div class="day"><div class="dayname" id="dayname"></div><div class="focus" id="focus"></div></div>
  <button class="navbtn" id="next" type="button">Next &#9654;</button>
</nav>
<nav>
  <button class="navbtn alt" id="todayBtn" type="button">Today</button>
  <button class="navbtn alt" id="weekBtn" type="button">This week</button>
</nav>
<main id="main"></main>

<div id="overlay" role="dialog" aria-modal="true">
  <button id="back" type="button">&#11013; Back</button>
  <div id="nowplaying"></div>
  <div id="playerWrap"></div>
</div>

<script id="lineup-data" type="application/json">__DATA_JSON__</script>
<script>
(function () {
  var DATA = JSON.parse(document.getElementById('lineup-data').textContent);
  var TZ = DATA.timezone || 'America/Chicago';
  var ICON = { sun: '\u2600\uFE0F', afternoon: '\uD83C\uDF07', star: '\u2B50' };
  var main = document.getElementById('main');
  var overlay = document.getElementById('overlay');
  var wrap = document.getElementById('playerWrap');
  var nowEl = document.getElementById('nowplaying');
  var player = null, pending = null, queue = [], qi = 0;

  // ---- dates (all as YYYY-MM-DD strings; arithmetic in UTC to avoid DST drift)
  function todayStr() {
    var p = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' })
      .formatToParts(new Date());
    var o = {}; p.forEach(function (x) { o[x.type] = x.value; });
    return o.year + '-' + o.month + '-' + o.day;
  }
  function toDate(s) { var a = s.split('-'); return new Date(Date.UTC(+a[0], +a[1] - 1, +a[2])); }
  function fmt(d) { return d.toISOString().slice(0, 10); }
  function addDays(s, n) { var d = toDate(s); d.setUTCDate(d.getUTCDate() + n); return fmt(d); }
  function dow(s) { return toDate(s).getUTCDay(); }
  function niceDate(s, short) {
    return toDate(s).toLocaleDateString('en-US', { timeZone: 'UTC', weekday: short ? 'short' : 'long', month: 'short', day: 'numeric' });
  }
  function weekFor(s) {
    for (var i = 0; i < DATA.weeks.length; i++) { var w = DATA.weeks[i]; if (s >= w.start && s <= w.end) return w; }
    return null;
  }
  var allDates = Object.keys(DATA.days).sort();
  var firstDate = DATA.weeks.length ? DATA.weeks[0].start : allDates[0];
  var lastDate = DATA.weeks.length ? DATA.weeks[DATA.weeks.length - 1].end : allDates[allDates.length - 1];
  function nearestWeek(s) { // week containing s, else latest week before s, else first week
    var w = weekFor(s); if (w) return w;
    var best = DATA.weeks[0];
    DATA.weeks.forEach(function (x) { if (x.start <= s) best = x; });
    return best;
  }
  function mins(sec) { return Math.round(sec / 60); }
  function mmss(sec) { var m = Math.floor(sec / 60), s = sec % 60; return m + ':' + (s < 10 ? '0' : '') + s; }
  function okId(id) { return /^[A-Za-z0-9_-]{11}$/.test(id); }

  // ---- rendering
  var current = null;
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function card(v, n, list, idx, segLabel) {
    var b = el('div', 'card');
    b.setAttribute('role', 'button'); b.tabIndex = 0;
    b.innerHTML = '<div class="thumb"><img alt="" loading="lazy"><span class="play"></span><span class="num"></span><span class="dur"></span></div>' +
                  '<div class="info"><div class="title"></div><span class="tag"></span></div>';
    b.querySelector('img').src = 'https://i.ytimg.com/vi/' + v.id + '/hqdefault.jpg';
    b.querySelector('.num').textContent = n;
    b.querySelector('.dur').textContent = v.seconds ? mmss(v.seconds) : (v.minutes + ' min');
    b.querySelector('.title').textContent = v.title;
    b.querySelector('.tag').textContent = v.tag || '';
    function go() { playList(list, idx, segLabel); }
    b.addEventListener('click', go);
    b.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
    return b;
  }

  function segmentBox(cls, icon, label, videos, prompt, target) {
    var vids = (videos || []).filter(function (v) { return okId(v.id); });
    var sec = el('section', 'seg ' + cls);
    var head = el('div', 'seghead');
    head.appendChild(el('span', 'icon', icon));
    head.appendChild(el('span', 'seglabel', label));
    var total = vids.reduce(function (a, v) { return a + (v.seconds || Math.round((v.minutes || 0) * 60)); }, 0);
    head.appendChild(el('span', 'segmins', mins(total) + ' min' + (target ? ' \u00B7 goal ' + target : '')));
    if (vids.length) {
      var pa = el('button', 'playall', '\u25B6 Play all');
      pa.type = 'button';
      pa.addEventListener('click', function () { playList(vids, 0, label); });
      head.appendChild(pa);
    }
    sec.appendChild(head);
    if (prompt) { var p = el('div', 'prompt'); p.appendChild(el('b', null, 'Car talk: ')); p.appendChild(document.createTextNode(prompt)); sec.appendChild(p); }
    var cards = el('div', 'cards');
    vids.forEach(function (v, i) { cards.appendChild(card(v, i + 1, vids, i, label)); });
    sec.appendChild(cards);
    return sec;
  }

  function setHeader(s, focus) {
    var w = nearestWeek(s);
    document.getElementById("weektitle").textContent = w ? w.title : '';
    var dn = document.getElementById('dayname');
    dn.textContent = niceDate(s);
    if (s === todayStr()) dn.appendChild(el('span', 'today-pill', 'Today'));
    document.getElementById('focus').textContent = focus || '';
    document.getElementById('prev').disabled = s <= firstDate;
    document.getElementById('next').disabled = s >= lastDate;
  }

  function showDay(s) {
    current = s; main.innerHTML = '';
    var day = DATA.days[s];
    if (day) {
      setHeader(s, day.focus);
      DATA.segments.forEach(function (sg) {
        var x = day.segments[sg.key];
        if (!x) return;
        main.appendChild(segmentBox('s-' + sg.key, ICON[sg.icon] || '', sg.label, x.videos, x.prompt, sg.target));
      });
      return;
    }
    // Weekend / no lineup: show the week's favorites.
    var w = nearestWeek(s), wk = w && w.weekend;
    var isWeekend = dow(s) === 0 || dow(s) === 6;
    var note = !weekFor(s) ? 'New lineup coming soon - here are some favorites'
             : isWeekend ? ((wk && wk.note) || 'Weekend!') : 'No lineup for this day yet - here are some favorites';
    setHeader(s, note);
    if (wk) main.appendChild(segmentBox('s-weekend', ICON.star, wk.title || 'Weekend favorites', wk.videos, null, null));
    else main.appendChild(el('div', 'empty', 'No videos for this day yet.'));
  }

  function showWeek(s) {
    current = s; main.innerHTML = '';
    var w = nearestWeek(s);
    document.getElementById("weektitle").textContent = w ? w.title : '';
    document.getElementById('dayname').textContent = 'This week';
    document.getElementById('focus').textContent = 'Tap a day to open it';
    document.getElementById('prev').disabled = !w || w.start <= firstDate;
    document.getElementById('next').disabled = !w || w.end >= lastDate;
    var start = w ? w.start : s; // weeks start on Monday
    var g = el('div', 'weekgrid'); g.appendChild(el('div', 'wcell whead', ''));
    var t = todayStr(), dates = [];
    for (var i = 0; i < 5; i++) dates.push(addDays(start, i));
    dates.forEach(function (d) {
      var h = el('button', 'wcell whead' + (d === t ? ' is-today' : ''), niceDate(d, true));
      h.type = 'button';
      h.addEventListener('click', function () { location.hash = d; });
      g.appendChild(h);
    });
    DATA.segments.forEach(function (sg) {
      var lab = el('div', 'wcell wseg s-' + sg.key, (ICON[sg.icon] || '') + ' ' + sg.label); g.appendChild(lab);
      dates.forEach(function (d) {
        var c = el('div', 'wcell'), ul = el('ul');
        var x = DATA.days[d] && DATA.days[d].segments[sg.key];
        (x ? x.videos : []).forEach(function (v) { ul.appendChild(el('li', null, v.title)); });
        c.appendChild(ul); c.style.cursor = 'pointer';
        c.addEventListener('click', function () { location.hash = d; });
        g.appendChild(c);
      });
    });
    main.appendChild(g);
    if (w && w.weekend) main.appendChild(segmentBox('s-weekend', ICON.star, w.weekend.title || 'Weekend favorites', w.weekend.videos, w.weekend.note, null));
  }

  // ---- routing: #YYYY-MM-DD or #week or #week-YYYY-MM-DD; default = today (Chicago)
  function route() {
    var h = location.hash.replace(/^#/, '');
    var m = /^week(?:-(\d{4}-\d{2}-\d{2}))?$/.exec(h);
    if (m) showWeek(m[1] || current || todayStr());
    else showDay(/^\d{4}-\d{2}-\d{2}$/.test(h) ? h : todayStr());
    window.scrollTo(0, 0);
  }
  function inWeekView() { return /^#week/.test(location.hash); }
  document.getElementById('prev').addEventListener('click', function () {
    if (inWeekView()) { location.hash = 'week-' + addDays(nearestWeek(current).start, -7); return; }
    location.hash = addDays(current, -1);
  });
  document.getElementById('next').addEventListener('click', function () {
    if (inWeekView()) { location.hash = 'week-' + addDays(nearestWeek(current).start, 7); return; }
    location.hash = addDays(current, 1);
  });
  document.getElementById('todayBtn').addEventListener('click', function () {
    if (location.hash === '' || location.hash === '#') route(); else location.hash = '';
  });
  document.getElementById('weekBtn').addEventListener('click', function () { location.hash = 'week-' + (current || todayStr()); });
  window.addEventListener('hashchange', route);
  // If the page is left open overnight, roll to the new day when no date is pinned.
  var lastToday = todayStr();
  setInterval(function () {
    var t = todayStr();
    if (t !== lastToday) { lastToday = t; if (!location.hash && !overlay.classList.contains('open')) route(); }
  }, 60000);

  // ---- player (youtube-nocookie, rel=0, closes at end; autoplays next video in the same segment)
  function playList(list, idx, label) { queue = list; qi = idx; openVideo(label); }
  function openVideo(label) {
    var v = queue[qi];
    closePlayer();
    var src = 'https://www.youtube-nocookie.com/embed/' + v.id +
              '?rel=0&modestbranding=1&playsinline=1&autoplay=1&enablejsapi=1';
    if (v.start) src += '&start=' + v.start;
    if (v.end) src += '&end=' + v.end;
    if (location.protocol === 'http:' || location.protocol === 'https:') {
      src += '&origin=' + encodeURIComponent(location.origin);
    }
    var f = document.createElement('iframe');
    f.id = 'ytframe'; f.src = src;
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true; f.referrerPolicy = 'strict-origin-when-cross-origin';
    wrap.appendChild(f);
    nowEl.textContent = (label ? label + '  \u2022  ' : '') + (qi + 1) + ' of ' + queue.length + ': ' + v.title;
    nowEl.dataset.label = label || '';
    overlay.classList.add('open');
    attachApi(f);
  }
  function attachApi(f) {
    if (!(window.YT && YT.Player)) { pending = f; return; }
    player = new YT.Player(f, { events: { onStateChange: function (e) {
      if (e.data !== YT.PlayerState.ENDED) return;
      if (qi + 1 < queue.length) { qi++; openVideo(nowEl.dataset.label); } else closeVideo();
    } } });
  }
  window.onYouTubeIframeAPIReady = function () {
    if (pending && pending.isConnected) attachApi(pending);
    pending = null;
  };
  function closePlayer() {
    if (player && player.destroy) { try { player.destroy(); } catch (e) {} }
    player = null; pending = null; wrap.innerHTML = '';
  }
  function closeVideo() { closePlayer(); queue = []; overlay.classList.remove('open'); }
  document.getElementById('back').addEventListener('click', closeVideo);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeVideo(); });

  route();
})();
</script>
<script src="https://www.youtube.com/iframe_api" async></script>
</body>
</html>
"""


def clean_video(v, where):
    vid = str(v["id"])
    if not ID_RE.match(vid):
        sys.exit(f"{where}: bad YouTube id {vid!r}")
    out = {"id": vid, "title": str(v["title"]), "tag": str(v.get("tag", ""))}
    if v.get("channel"):
        out["channel"] = str(v["channel"])
    for k in ("start", "end"):  # optional chunk of a long video, in seconds
        if v.get(k) is not None:
            out[k] = int(v[k])
    if v.get("seconds"):
        out["seconds"] = int(v["seconds"])
    if v.get("minutes") is not None:
        out["minutes"] = float(v["minutes"])
    elif "seconds" in out:
        out["minutes"] = round(out["seconds"] / 60, 1)
    else:
        sys.exit(f"{where}: video {vid} needs 'minutes' or 'seconds'")
    return out


def check_date(s, where):
    if not DATE_RE.match(s):
        sys.exit(f"{where}: bad date {s!r} (use YYYY-MM-DD)")
    dt.date.fromisoformat(s)


def main():
    data = json.loads((HERE / "lineup.json").read_text(encoding="utf-8"))
    clean = {"timezone": data.get("timezone", "America/Chicago"), "segments": [], "weeks": [], "days": {}}
    for s in data["segments"]:
        if s["key"] not in SEG_KEYS:
            sys.exit(f"Unknown segment key {s['key']!r}")
        clean["segments"].append({k: str(s[k]) for k in ("key", "label", "icon", "target", "who") if k in s})
    for w in sorted(data["weeks"], key=lambda w: w["start"]):
        check_date(w["start"], "week"); check_date(w["end"], "week")
        cw = {"start": w["start"], "end": w["end"], "title": str(w["title"])}
        if w.get("weekend"):
            wk = w["weekend"]
            cw["weekend"] = {"title": str(wk.get("title", "Weekend favorites")), "note": str(wk.get("note", "")),
                             "videos": [clean_video(v, f"weekend {w['start']}") for v in wk.get("videos", [])]}
        clean["weeks"].append(cw)
    warnings = []
    for d in sorted(data["days"]):
        check_date(d, "day")
        day = data["days"][d]
        cd = {"focus": str(day.get("focus", "")), "segments": {}}
        for key in SEG_KEYS:
            seg = day["segments"].get(key)
            if not seg:
                warnings.append(f"{d}: missing segment {key}")
                continue
            vids = [clean_video(v, f"{d}/{key}") for v in seg["videos"]]
            total = sum(v.get("seconds", v["minutes"] * 60) for v in vids) / 60
            lo, hi = SEG_RANGE[key]
            if not lo <= total <= hi:
                warnings.append(f"{d}/{key}: {total:.1f} min (target {lo}-{hi})")
            cd["segments"][key] = {"prompt": str(seg.get("prompt", "")), "videos": vids}
        if not any(w["start"] <= d <= w["end"] for w in clean["weeks"]):
            warnings.append(f"{d}: not inside any week")
        clean["days"][d] = cd
    # Safe to embed inside <script>: escape '<' so '</script>' can't break out.
    blob = json.dumps(clean, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    week_title = clean["weeks"][-1]["title"] if clean["weeks"] else ""
    import html
    out = TEMPLATE.replace("__WEEK_HTML__", html.escape(week_title)).replace("__DATA_JSON__", blob)
    (HERE / "index.html").write_text(out, encoding="utf-8")
    for w in warnings:
        print("warning:", w)
    print(f"Wrote {HERE / 'index.html'} ({len(clean['days'])} days, {len(clean['weeks'])} weeks)")


if __name__ == "__main__":
    main()
