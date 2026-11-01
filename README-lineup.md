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

Player: a youtube-nocookie embed with `rel=0`. **Play all** (or tapping a card) plays that segment in order. Nothing is locked: every clip can be skipped, and every segment can be opened in any order.

Anti-derail features (they keep the plan visible, and they don't block anything):
- **Up next panel**: after each clip (when it ends, or on Skip) the player stays open and shows **Next in today's ride** plus **Back to today's plan**. If the clip has an `ask`, the question is shown and the player waits. If not, it continues by itself after 8 seconds. When a segment ends, it shows the checkpoint, a button for the next segment in the same ride, and the Boys' pick buttons.
- **Progress strip**: dots in the player ("1 of 4") and an "n of N done" line on each segment. Progress is saved in this browser only (localStorage `kl-progress`), and **Play all** becomes **Continue (k of N)**.
- **Skip ⏭** (top right of the player): marks the clip as skipped and moves to the next clip *in the planned order*. It never jumps to a random video.
- **Two-clip rule**: from Nov 2 on, the build warns if a segment has 2 clips in a row with no `ask`. The player also shows a generic question after 2 clips with no ask. Put favorites (Numberblocks, LEGO) first or in between, not all at the end.
- **Boys' pick**: 2-3 checked choices per ride for after the plan (`weeks[].picks`). They show on the Little Brother, Big Brother and afternoon Together segments.
- **Checkpoint**: one line at the end of each segment (`checkpoint` on the day segment, falling back to `segments[].checkpoint`).

**If a clip gets skipped:** that's fine. Say its `ask` out loud anyway (or the car-talk line), then go on to the next clip. Don't search YouTube for a replacement in the car. If a whole segment is skipped, use its checkpoint line as the car-talk.

**Ride order:** morning = Together, then Little Brother. Afternoon = Big Brother, then Together. In each segment: play the clips in order, then the question, then the checkpoint, then (optional) one Boys' pick.

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
- `start` / `end` (optional, seconds): play only a chunk of a long video. Set `seconds` to the chunk length (end - start).
- `seconds` (preferred) or `minutes`: the real length. The page shows mm:ss on each card and adds up a total per segment.

`build.py` warns (it doesn't fail) when a segment's total runs outside its soft range: amTogether 3-7, amYounger 9-16, pmOlder 9-18, pmTogether 3-9 minutes.

Optional fields (all of them pass through `build.py`):
- video `ask`: a one-line question shown under the card and in the Up next panel.
- day segment `checkpoint` (string) and `pick` (list of videos): override the week's picks for that segment.
- `segments[].checkpoint`: the default end-of-segment line.
- `weeks[].picks`: `{"together": [...], "younger": [...], "older": [...]}`, 2-3 checked videos each.

## Adding a new week

1. **Pick videos** from reputable kid channels: SciShow Kids, Crash Course Kids, Peekaboo Kidz, Numberblocks, Alphablocks, PBS KIDS, Odd Squad, Mark Rober, CrunchLabs, Brick Experiment Channel, Khan Academy, Seeker, ChessKid, Science Max, Scratch Team, Scratch Garden, MightyOwl, and similar. Don't use Shorts, parodies, reaction channels, or game-drama channels.

   **Tone rules** (both boys find babyish content boring; Numberblocks is the exception they still love):
   - No preschool songs (Jack Hartmann, Pinkfong, Sesame songs), no cutesy read-alouds (StorylineOnline), no toddler cartoons (Masha), no sing-song 'meditation' clips.
   - Never use Jack Hartmann for any slot (Big Brother dislikes him), including in faith, art, math, and movement items.
   - Story time is a **parent-led story**, a **real-story audiobook**, a **documentary/science clip**, or a **challenge**.
   - Frame it the way builders do: test, measure, predict, explain, without drama. Use LEGO, Scratch, engineering, sports, chess, puzzles, real places and history, and saints as heroes.
   - Big Brother (7): a real story plus a big question. Little Brother (5): hands-on and capable, not babyish.
   - Write copy in a capable voice: "sketch it and label it", "prove it with bricks", "predict, then test". Avoid "use your fingers!" and "say it like Masha".
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

## Faith strand (`faith` in `lineup.json`)

A light, separate strand: **Faith: Jesus & the Catholic Church**. It's about 10 minutes on Tue and Thu after school, an optional Saturday build, and a Sunday family moment. It is **not** part of the car rides. Open it with the **✝ Faith** button, `#faith` (the current faith week), or `#faith-2026-11-16`. Prev/Next step one faith week at a time. A small Faith strip also appears under the **This week** grid and on weekend days.

```jsonc
"faith": {
  "title": "Faith: Jesus & the Catholic Church",
  "rhythm": "About 10 minutes: Tue and Thu ...",
  "weeks": [
    {"start": "2026-11-02", "end": "2026-11-08", "title": "Part 1 - ...",
     "liturgy": "Sun Nov 1 All Saints · Mon Nov 2 All Souls",
     "bigIdea": "One or two sentences, with a Bible reference",
     "videos": [ VIDEO + "ask" (discussion prompt shown on the card), optional "day" and "note" (source caveat) ],  // 2-3
     "activity": {"younger": "hands-on, not babyish", "older": "real story + big question"},
     "sunday": "Sunday family moment"}
  ],
  "reference": [ {"title": "...", "lines": ["..."], "links": [{"label": "...", "url": "https://..."}]} ]
}
```

Faith sources: prefer Catholic channels (Loyola Press, Catholic Central, Father Roderick - LEGO Brickpriest, Ascension, diocesan channels). If you use a general history, travel or nature clip, say so in `note`. Be accurate to Catholic teaching. Skip toddler cartoons and graphic martyrdom stories.
