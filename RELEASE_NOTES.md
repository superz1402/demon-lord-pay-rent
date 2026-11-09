# Episode 1 — “The Rent Must Flow” (v0.1.0)

First public release of **魔王、家賃を払え！ / DEMON LORD, PAY RENT!** —
a funny anime sitcom written as React/TypeScript and rendered by
[raea](https://github.com/shinyobjectz/raea) on your GPU. No video models.

## The premise

Xargoth the Unending conquered 108 worlds, got bored, moved to Earth — and is
**¥284,000 behind on rent**. His roommate Kenji holds the Rent Envelope™.
The cat is the hero who sealed him 800 years ago. He will not confirm.

## Release assets

| Asset | What it is |
|---|---|
| `dlpr_animatic_preview.mp4` | **Watch this** — the full 51s episode-1 package (cold open → OP → eyecatch → end card) as a rough animatic with the synthesized funk theme. Plays anywhere, no raea needed. |
| `demon-lord-pay-rent.zip` | The complete raea project (same as this repo, zipped, includes `theme.wav`). |
| `theme.mp3` | The 51s sitcom-funk theme bed, pre-timed to picture. |

## What's in the repo

- `src/scenes/` — ColdOpen (600f), Op (540f), Eyecatch (150f), EndCard (240f) @30fps, 1920×1080
- `src/characters/` — Xargoth, Kenji, SeniorTheCat (flat-cel SVG, ink outlines)
- `src/Fx.tsx` — speed lines, ゴゴゴ menace, ドン impact, laugh-beat cards, subtitles
- `docs/EPISODE_01.md` — director's beat sheet + full scripts for Episodes 1–2
- `public/audio/theme.mp3` — 51s music bed

## Quick start

```sh
curl -fsSL https://raea.io/install | sh
raea render src/scenes/Op.tsx -o out/op.mp4
```

Full pipeline (all four pieces + stitching + `raea check`) in [README.md](README.md).

## Credits

- Screenplay — THE CAT
- Music — CONVENIENCE STORE SPEAKERS
- Catering — 100 YEN SHOP
- Rendering — raea (FSL-1.1-ALv2), no affiliation
