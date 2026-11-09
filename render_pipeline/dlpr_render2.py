#!/usr/bin/env python3
"""DLPR Ep2 FULL — main renderer. Parallel frames -> ffmpeg -> video.h264.

Usage:
  python3 dlpr_render2.py preview     # render sample frames as PNGs
  python3 dlpr_render2.py full        # render all 7098 frames -> video.h264
"""
import subprocess, sys, os, time
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)


def _init():
    global R
    import dlpr_segs2 as R


def _render(args):
    g, path = args
    img = R.render_frame(g)
    if path:
        img.save(path)
        return g, None
    return g, img.tobytes()


PREVIEW_FRAMES = [
    30, 300, 430, 590, 655,          # cold: establish / ritual / kenji truth / freeze / title
    700, 760, 830, 910, 1050,        # op: logo / xar card / kenji card / cat card / group
    1130,                            # finale
    1300, 1420, 1500,                # A1: morning / plan card / pose
    2000, 2150, 2330, 2500, 2700,    # A2: menace / rite zap / hope green / die
    2900, 3100, 3350, 3700,          # A3: cards / beeps / lockout / laugh
    4100, 4400, 4600, 4900,          # A4: tray / shadow / note / collapse
    5250, 5500, 5650, 5900,          # B1 receipt / coins / pudding abyss
    6100, 6300, 6500, 6700,          # B2 bid board / union / microwave war
    6950, 7000, 7040,                # B3 countdown / drop / stamp
    7050, 7080,                      # B3 silence
    6950, 7050, 7080, 6900,          # (dupes trimmed below)
    6900, 7050, 7080,                # B4 obaa / tsuzuku
    7150, 7300, 7400,                # end card
]
PREVIEW_FRAMES = sorted(set(f for f in PREVIEW_FRAMES if f < 7098))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        jobs = [(g, os.path.join(ROOT, "preview", f"f{g:05d}.png"))
                for g in PREVIEW_FRAMES]
        with Pool(2, initializer=_init) as p:
            for g, _ in p.imap_unordered(_render, jobs):
                print("preview", g, flush=True)
        print("previews written to", os.path.join(ROOT, "preview"))
        return
    # full render
    total = TL_TOTAL()
    out_h264 = os.path.join(ROOT, "video.h264")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x720", "-r", "30",
           "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-an", out_h264]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    done = 0
    with Pool(2, initializer=_init) as p:
        for g, buf in p.imap(_render, [(g, None) for g in range(total)], chunksize=8):
            proc.stdin.write(buf)
            done += 1
            if done % 300 == 0:
                el = time.time() - t0
                print(f"frame {done}/{total}  {el:.0f}s  eta {el/done*(total-done):.0f}s",
                      flush=True)
    proc.stdin.close(); proc.wait()
    print("wrote", out_h264, f"in {time.time()-t0:.0f}s")


def TL_TOTAL():
    import json
    tl = json.load(open(os.path.join(ROOT, "timeline.json")))
    return tl["total_frames"]


if __name__ == "__main__":
    main()
