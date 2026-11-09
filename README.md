# 魔王、家賃を払え！ — *DEMON LORD, PAY RENT!*

A funny **anime sitcom** built as code for [raea](https://github.com/shinyobjectz/raea),
the Render Anything Engine. No video models — just React/TypeScript compositions
rendered **on your GPU**, faster than real time.

> The premise: Xargoth the Unending conquered 108 worlds, got bored, moved to
> Earth — and is three months behind on rent. His roommate Kenji holds the
> Rent Envelope™. The cat is the hero who sealed him 800 years ago (won't
> confirm). Rent day is monthly, so the sitcom writes itself.

**Full script & director's beat sheet:** [`docs/EPISODE_01.md`](docs/EPISODE_01.md)

---

## What's in the box

```
src/
  style.ts                  style bible: palette, timing, easing helpers
  ApartmentSet.tsx          the apartment 302 set (consistent sitcom blocking)
  Fx.tsx                    speed lines, ゴゴゴ menace, ドン impact, laugh-beat cards, subtitles
  characters/
    Xargoth.tsx             the demon lord (smug / panic / sparkle)
    Kenji.tsx               the straight man + The Rent Envelope™
    SeniorTheCat.tsx        the cat (definitely not the hero)
  scenes/
    ColdOpen.tsx            20s — cold open w/ freeze-frame 4th-wall gag  (600 frames)
    Op.tsx                  18s — anime OP: logo slam, 3 character cards, group shot (540 frames)
    Eyecatch.tsx             5s — chibi A-part bumper                        (150 frames)
    EndCard.tsx              8s — next-episode preview                       (240 frames)
  Root.tsx                  composition registry (optional style)
public/audio/theme.mp3      51s synthesized sitcom-funk bed (already mixed to picture)
docs/EPISODE_01.md          script + shot list + style bible
```

**Watch the FULL EPISODE:** `dlpr_episode1_full.mp4` (3:56, 720p) — the complete
Episode 1 with **full voice narration** (6 TTS voices: the cat narrator, Xargoth,
Kenji, the manager, a customer and Landlord Obaa-san), a 237s original score and
synthesized SFX, rendered by the code pipeline in [`render_pipeline/`](render_pipeline/).
The older `dlpr_animatic_preview.mp4` (51s) is the original rough animatic.

---

## Render it (macOS / Linux / Windows)

**1. Install raea** (free, no account):

```sh
curl -fsSL https://raea.io/install | sh        # macOS / Linux
irm https://raea.io/install.ps1 | iex          # Windows (PowerShell)
```

**2. Render each piece** (each scene file is self-contained):

```sh
cd demon-lord-pay-rent
raea render src/scenes/ColdOpen.tsx -o out/cold-open.mp4
raea render src/scenes/Op.tsx        -o out/op.mp4
raea render src/scenes/Eyecatch.tsx  -o out/eyecatch.mp4
raea render src/scenes/EndCard.tsx   -o out/end-card.mp4
```

> raea is canary and its registry style may differ. If a bare scene file
> doesn't render, uncomment the `registerRoot` line at the bottom of that
> scene file, or point raea at `src/Root.tsx` (a `<Composition id component
> durationInFrames fps width height>` variant is provided in comments there).
> When in doubt, `raea guide` prints the canonical composition form for
> your build — it ships with the engine for exactly this.

**3. Stitch + add music** (theme.mp3 is pre-timed to the 4 pieces):

```sh
printf "file 'cold-open.mp4'\nfile 'op.mp4'\nfile 'eyecatch.mp4'\nfile 'end-card.mp4'\n" > out/list.txt
ffmpeg -f concat -safe 0 -i out/list.txt -i public/audio/theme.mp3 \
       -c:v copy -map 0:v -map 1:a -shortest out/episode-1-nomix.mp4
```

(If your raea build accepts audio natively in compositions, follow
`raea guide sound` instead — the mixer is the more raea-native path.)

**4. Quality pass** — raea's built-in checker catches clipped text, low
contrast, unsafe areas, freezes and loudness:

```sh
raea check out/episode-1.mp4
```

---

## Episodes

- **Episode 1 — The Rent Must Flow** · full cut released as `v1.0.0`
- **Episode 2 — The Abyssal Wi-Fi Password** · full cut released as `v1.1.0`
  (55 voiced lines, 6 voices; the landlady buys back the cursed crown, the
  password was on the lease all along, the cat was hogging the router)

## Extend it

- **Episode 2 pipeline lives in `render_pipeline/`** (`dlpr_lines2.py` →
  `timeline_ep2.json` → `dlpr_score2.py` / `dlpr_segs2.py` / `dlpr_render2.py`
  / `dlpr_mix2.py`). Episode 3 ("Demon Lord, Night Shift", teased on the Ep2
  end card) reuses the same skeleton: same segment map, new lines + seg code.
- New gags = new frames in a scene file; every joke sits on a numbered
  beat, so retiming a punchline is moving one constant.
- New characters: copy `SeniorTheCat.tsx`, keep the 6–8px ink outline and
  two-tone shadow rule from the style bible, and the show stays consistent.
- Sitcom rule encoded in `style.ts`: **the couch never moves** — only the
  demon lord's dignity does.

## License note

raea itself is FSL-1.1-ALv2 (free to use, no telemetry). This show package
is yours — do whatever, just pay your rent.

---

## Publishing this repo (create + push + release in one command)

This checkout is already git-initialized and tagged `v0.1.0`. To publish:

```sh
export GITHUB_TOKEN=github_pat_...   # fine-grained PAT, see scopes below
./push_and_release.sh
```

The script creates `shinyobjectz/demon-lord-pay-rent`, pushes `main` + the tag,
creates release **"Episode 1 — The Rent Must Flow"** and uploads
`dlpr_animatic_preview.mp4`, `demon-lord-pay-rent.zip` and `theme.mp3` as
release assets (set `ASSET_DIR` to wherever those files are).

**Token scopes (fine-grained PAT):**
- Repository access: *All repositories* (needed to create a new one)
- Permissions: **Administration → Read & write** (repo creation),
  **Contents → Read & write** (push + release upload)
- Short expiry recommended; revoke after the push.

Commit author is set to `shinyobjectz@users.noreply.github.com` — amend if
you prefer your own identity.
