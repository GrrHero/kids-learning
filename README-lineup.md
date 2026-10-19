# Kids Learning: daily car-ride lineup

`index.html` is one self-contained page. **Don't edit it by hand.** Edit `lineup.json`, then run `python3 build.py`, which checks the data and writes `index.html` with the data inlined.

The page opens on **today** (America/Chicago time) and shows four sections:

| key          | label on page              | who            | target    |
|--------------|----------------------------|----------------|-----------|
| `amTogether` | Morning - Together         | both           | ~5 min    |
| `amYounger`  | Morning - Little Brother   | younger (K)    | 10-15 min |
| `pmOlder`    | Afternoon - Big Brother    | older (2nd)    | 10-15 min (can stretch to ~17) |
| `pmTogether` | Afternoon - Together       | both           | ~5 min (read-alouds up to ~8) |

Buttons: big **Prev / Next** (one day at a time, limited to the dates in `weeks`), **Today**, and **This week** (a Mon-Fri grid plus the weekend favorites). On a Saturday or Sunday, or any date with no `days` entry, the page shows that week's `weekend` list instead.
Deep links: `#2026-10-21` opens a day, `#week` opens the current week, `#week-2026-10-26` opens a given week.

Player: a youtube-nocookie embed with `rel=0`. **Play all** (or tapping a card) plays that segment in order and auto-advances to the next video in the *same* segment. The player closes after the segment's last video, and **Back** closes it at any time.

## Data format (`lineup.json`)

```jsonc
{
  "timezone": "America/Chicago",
  "segments": [            // order = order on the page; keys must be the four above
    {"key": "amTogether", "label": "Morning - Together", "who": "Both brothers", "icon": "sun", "target": "~5 min"},
    ...                    // icon: "sun" | "afternoon" | "star"
  ],
  "weeks": [
    {"start": "2026-10-19", "end": "2026-10-25",          // Monday .. Sunday
     "title": "Week 1: Pushes & Pulls (Oct 19-25)",
     "weekend": {"title": "Weekend favorites",
                 "note": "Saturday Art Studio: LINE. Sunday bonus: ...",
                 "videos": [ VIDEO, ... ]}}
  ],
  "days": {
    "2026-10-19": {
      "focus": "Pushes & Pulls · Break it down · LEGO beam bridge",   // one line under the date
      "segments": {
        "amTogether": {"prompt": "Car-talk question", "videos": [ VIDEO, ... ]},
        "amYounger":  {...}, "pmOlder": {...}, "pmTogether": {...}
      }
    }
  }
}
```

VIDEO:

```json
{"id": "5-2NLHB4Gxg", "title": "What Is Force? (Dr. Binocs)", "channel": "Peekaboo Kidz",
 "tag": "Sci 2.7A Force & motion", "seconds": 363, "minutes": 6.0}
```

- `id`: the 11-character YouTube id. `build.py` rejects anything else.
- `title`: a short, kid-friendly display title (it doesn't have to match YouTube's full title).
- `tag`: a short Texas TEKS strand tag. Conventions: `Sci K.7` magnets/push-pull (K), `Sci 2.7` force & motion, `Sci 2.1` science & engineering practices, `Math K.2` counting, `Math K.3` add/sub stories, `Math K.6` shapes, `Math 2.2` place value, `Math 2.4C` add/sub word problems, `Math 2.7` patterns/number reasoning, `Math 2.8` geometry, `ELAR K.2` phonics, `ELAR K.6/2.6` retell/comprehension, `ELAR 2.8` story elements/plot, `Tech Apps: coding`, `Fine Arts: <element>`, `SEL` (not TEKS).
- `seconds` (preferred) or `minutes`: the real length. The page shows mm:ss on each card and adds up a total per segment.

`build.py` warns (it doesn't fail) when a segment's total runs outside its soft range: amTogether 3-7, amYounger 9-16, pmOlder 9-18, pmTogether 3-9 minutes.

## Adding a new week

1. **Pick videos** from reputable kid channels: SciShow Kids, Crash Course Kids, Peekaboo Kidz, Numberblocks, Alphablocks, Jack Hartmann, PBS KIDS, Odd Squad, StorylineOnline, Mark Rober, Scratch Team, Scratch Garden, MightyOwl, and similar. Don't use Shorts, parodies, reaction channels, or game-drama channels.
2. **Verify every id** (no exceptions):
   ```
   python3 tools/verify_videos.py ID1 ID2 ...
   ```
   Each line prints the channel, YouTube title, duration and `embed=True/False`. Use a video only if the channel and title are what you expect **and** `embed=True`. Results, including `seconds`, are saved in `tools/verified.json`.
3. **Add the week** to `weeks` (Mon-Sun, with a `weekend` list), and add 5 `days` entries (Mon-Fri) with all four segments. Copy `seconds` from `tools/verified.json`.
4. Run `python3 build.py`. Fix any errors and look over the warnings.
5. **Preview** (headless, 1280x800; `preview.png` is gitignored):
   ```
   google-chrome --headless=new --no-sandbox --hide-scrollbars --window-size=1280,800 \
     --virtual-time-budget=6000 --screenshot=preview.png "file://$PWD/index.html#2026-10-26"
   ```
6. Run `git add lineup.json index.html tools/verified.json && git commit -m "Week N lineup" && git push`. GitHub Pages updates in about a minute.

Weekly pattern (from the family agenda): Mon break it down + LEGO structures; Tue spot the pattern + Growth Skills (reading → word problem → self-check); Wed think aloud + Snap Circuits; Thu stuck practice (3 strategies) + Growth Skills; Fri teach-back + Scratch, with flexible fun picks (Mark Rober, LEGO, art, music, a favorite rewatch).

Keep the page free of personal information: no names, photos or school names. Use only generic labels like "Big Brother" and "Little Brother".
