#!/usr/bin/env python3
"""DLPR Ep1 FULL — final mix: narration + ducked score -> mux with video."""
import json, os, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 44100
tl = json.load(open(os.path.join(ROOT, "timeline.json")))
TOTAL = tl["total_sec"] + 0.6
N = int(SR * TOTAL)

# ---------- narration track ----------
narr = np.zeros((N, 2))
for L in tl["lines"]:
    path = os.path.join(ROOT, "audio_clips", f"{L['id']}.wav")
    with wave.open(path, "rb") as w:
        sr, ch, sw, nf = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
        raw = w.readframes(nf)
    assert sw == 2
    sig = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch == 2:
        sig = sig.reshape(-1, 2).mean(axis=1)
    # resample 24k -> 44.1k
    dur = len(sig) / sr
    tgt = int(dur * SR)
    if tgt < 2: continue
    x_old = np.linspace(0, dur, len(sig))
    x_new = np.linspace(0, dur, tgt)
    sig = np.interp(x_new, x_old, sig)
    i0 = int(L["start"] * SR)
    e = min(N, i0 + len(sig))
    if e <= i0: continue
    narr[i0:e, 0] += sig[:e - i0]
    narr[i0:e, 1] += sig[:e - i0]
print(f"narration track: {len(tl['lines'])} clips placed")

# gentle fade on the very tail
tail = int(0.8 * SR)
narr[-tail:] *= np.linspace(1, 0, tail)[:, None]

# ---------- duck envelope from narration ----------
env = np.abs(narr[:, 0]) + np.abs(narr[:, 1])
win = int(0.05 * SR)
kern = np.ones(win) / win
env = np.convolve(env, kern, mode="same")
env = np.clip(env / (env.max() + 1e-9), 0, 1)
# smooth attack/release
env = np.convolve(env, np.ones(int(0.12 * SR)) / int(0.12 * SR), mode="same")
duck = 1.0 - 0.74 * env  # music dips to ~26% under speech

# ---------- score ----------
with wave.open(os.path.join(ROOT, "score.wav"), "rb") as w:
    sr, ch = w.getframerate(), w.getnchannels()
    raw = w.readframes(w.getnframes())
sc = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
sc = sc.reshape(-1, 2)
m = min(N, len(sc))
score = np.zeros((N, 2))
score[:m] = sc[:m]

# ---------- master ----------
mix = narr * 1.05 + score * duck[:, None] * 0.9
mix = np.tanh(mix * 1.15) * 0.88
peak = np.max(np.abs(mix)) or 1.0
mix = mix / peak * 0.92
pcm = (mix * 32767).astype(np.int16)
out_wav = os.path.join(ROOT, "final_mix.wav")
with wave.open(out_wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", out_wav, f"{TOTAL:.1f}s peak={peak:.3f}")

# ---------- mux ----------
out_mp4 = "/home/z/my-project/download/dlpr_episode1_full.mp4"
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
       "-i", os.path.join(ROOT, "video.h264"),
       "-i", out_wav,
       "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
       "-shortest", "-movflags", "+faststart", out_mp4]
subprocess.run(cmd, check=True)
print("wrote", out_mp4)
