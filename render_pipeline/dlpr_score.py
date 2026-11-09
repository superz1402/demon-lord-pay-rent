#!/usr/bin/env python3
"""DLPR Episode 1 FULL — 235s stereo score + SFX, driven by timeline.json.

Sections (absolute seconds):
  cold 0-22     sparse pizzicato + gongs, snap shimmer, freeze scratch, smash
  op 22-40      funk @128, card stingers, group lift, finale fanfare
  apart 40-130  sitcom groove, horror sting, keyring rattle, anthem, sad-womp,
                interview muzak, laugh stabs
  eye 130-135   ba-dum-tss + bell arpeggio
  bpart 135-225 big groove, war sting, review sad, PAYDAY choir -> SILENCE beat
                -> warm pad, obaa doom, collapse gong
  end 225-235.2 outro chords, preview sting, final tag
Writes dlpr_build/score.wav (44.1k stereo).
"""
import json, os, subprocess
import numpy as np
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 44100

tl = json.load(open(os.path.join(ROOT, "timeline.json")))
EV = tl["events"]
DUR = tl["total_sec"] + 0.4
N = int(SR * DUR)
mixL = np.zeros(N)
mixR = np.zeros(N)
rng = np.random.default_rng(7)

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

def add(sig, t0, pan=0.0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0: return
    s = max(0, -i0); e = min(len(sig), N - i0)
    gl = gain * min(1.0, 1.0 - pan); gr = gain * min(1.0, 1.0 + pan)
    mixL[i0 + s:i0 + e] += sig[s:e] * gl
    mixR[i0 + s:i0 + e] += sig[s:e] * gr

def env(n, a=0.005, d=0.08, s=0.6, r=0.05, total=None):
    if total: n = int(total * SR)
    t = np.arange(n) / SR
    e = np.ones(n)
    an = max(1, int(a * SR)); dn = max(1, int(d * SR)); rn = max(1, int(r * SR))
    e[:an] = np.linspace(0, 1, an)
    if an + dn < n:
        e[an:an + dn] = np.linspace(1, s, dn)
        e[an + dn:] = s
    tail = np.clip((n - 1 - np.arange(n)) / rn, 0, 1)
    return e * tail

def tone(freq, dur, kind="tri", detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * freq * t * (1 + detune)
    if kind == "sine": return np.sin(ph)
    if kind == "tri": return 2 / np.pi * np.arcsin(np.sin(ph))
    if kind == "square": return np.sign(np.sin(ph)) * 0.6
    if kind == "saw": return ((freq * t) % 1.0) * 2 - 1
    return np.sin(ph)

def pluck(m, dur, kind="tri", gain=0.5, pan=0.0, t0=0.0):
    f = mtof(m)
    sig = tone(f, dur, kind) * env(int(dur * SR), a=0.004, d=0.10, s=0.35, r=0.08)
    add(sig, t0, pan, gain)

def gong(t0, base=38.0, gain=0.5):
    dur = 2.2
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for h, a in [(1, 1.0), (1.51, 0.6), (2.02, 0.4), (2.9, 0.25)]:
        sig += a * np.sin(2 * np.pi * base * h * t) * np.exp(-t * (1.6 + h))
    noise = np.random.default_rng(int(base * 100)).normal(0, 1, n) * np.exp(-t * 6) * 0.15
    add((sig + noise) * env(n, a=0.002, d=0.4, s=0.5, r=0.8), t0, 0.0, gain)

def kick(t0, gain=0.9):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = 150 * np.exp(-t * 28) + 42
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)
    add(sig, t0, 0.0, gain)

def snare(t0, gain=0.5):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    r2 = np.random.default_rng(int(t0 * 997) % (2**31))
    noise = r2.normal(0, 1, n) * np.exp(-t * 30)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * 0.5
    add(noise + body, t0, 0.0, gain)

def hat(t0, gain=0.18, dur=0.05):
    n = int(dur * SR)
    t = np.arange(n) / SR
    r2 = np.random.default_rng(int(t0 * 991) % (2**31))
    noise = np.diff(r2.normal(0, 1, n), prepend=0)
    add(noise * np.exp(-t * 60), t0, -0.3, gain)

def scratch(t0, dur=0.4, gain=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = np.random.default_rng(4242).normal(0, 1, n)
    f = 900 * np.exp(-t * 5) + 120
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = noise * (0.5 + 0.5 * np.sin(ph))
    sig *= env(n, a=0.002, d=0.2, s=0.5, r=0.1)
    add(sig, t0, 0.0, gain)

def brass_hit(t0, midis, gain=0.8, dur=0.9):
    for i, m in enumerate(midis):
        f = mtof(m)
        sig = tone(f, dur, "saw", detune=0.004) * 0.5 + tone(f, dur, "tri") * 0.5
        sig *= env(int(dur * SR), a=0.01, d=0.25, s=0.4, r=0.3)
        add(sig, t0, pan=(-0.4 + 0.8 * i / max(1, len(midis) - 1)), gain=gain / len(midis) * 2)

def chord(t0, midis, dur, kind="tri", gain=0.3, pan=0.0):
    for m in midis:
        pluck(m, dur, kind, gain / len(midis) * 1.6, pan, t0)

def rattle(t0, gain=0.5, n_ding=7):
    """Keyring: metallic dings in a hurry."""
    for i in range(n_ding):
        tt = t0 + i * 0.055 + rng.uniform(0, 0.02)
        f = 2600 + rng.uniform(-400, 700)
        n = int(0.09 * SR)
        t = np.arange(n) / SR
        sig = np.sin(2 * np.pi * f * t) * np.exp(-t * 55) * 0.8
        sig += np.sin(2 * np.pi * f * 2.7 * t) * np.exp(-t * 80) * 0.3
        add(sig, tt, rng.uniform(-0.4, 0.4), gain)

def crowd_puff(t0, gain=0.4):
    """Laugh-track-ish airy swell."""
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    noise = np.random.default_rng(int(t0 * 31) % (2**31)).normal(0, 1, n)
    noise = np.diff(noise, prepend=0)  # brighten
    band = noise * np.exp(-((t - 0.22) ** 2) / 0.02)
    add(band * env(n, a=0.05, d=0.1, s=0.6, r=0.25), t0, 0.0, gain)

def clock_tick(t0, gain=0.25):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 120)
    add(sig, t0, 0.2, gain)

def sad_womp(t0, gain=0.5):
    """Trombone-ish descending fail."""
    for i, m in enumerate([62, 59, 55]):
        f = mtof(m)
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        sig = tone(f, 0.5, "saw") * env(n, a=0.02, d=0.2, s=0.5, r=0.2)
        add(sig, t0 + i * 0.28, 0.0, gain * (1 - i * 0.2))

def choir_pad(t0, midis, dur, gain=0.4):
    for i, m in enumerate(midis):
        f = mtof(m)
        n = int(dur * SR)
        t = np.arange(n) / SR
        sig = np.sin(2 * np.pi * f * t) * 0.9 + 0.3 * np.sin(2 * np.pi * f * 1.01 * t)
        sig *= env(n, a=0.4, d=1.0, s=0.75, r=0.8)
        add(sig, t0, pan=(-0.5 + i / max(1, len(midis) - 1)), gain=gain / len(midis) * 1.8)

# ================= COLD (0-22) =================
for i, bt in enumerate(np.arange(0, EV["freeze_t"] - 1, 0.9375)):
    if i % 2 == 0:
        pluck(38 if (i // 2) % 2 == 0 else 45, 0.5, "tri", 0.40, 0.0, bt)
    if i % 4 == 3:
        pluck(50, 0.3, "square", 0.09, 0.2, bt)
pad = tone(mtof(38), EV["freeze_t"] - 1.5, "saw") * 0.5 + tone(mtof(45), EV["freeze_t"] - 1.5, "saw", 0.006) * 0.5
pad *= env(int(len(pad) / SR * SR) if len(pad) else 1, a=1.2, d=2.0, s=0.35, r=1.5)
add(pad * 0.09, 0.0, 0.0, 0.9)
gong(0.2); gong(6.0); gong(12.0)
for j in range(6):  # snap shimmer
    pluck(86 + j * 2, 0.12, "sine", 0.15, -0.3 + j * 0.12, EV["snap_t"] + j * 0.045)
scratch(EV["freeze_t"])
brass_hit(21.55, [50, 57, 62, 66], 0.95)
gong(21.55, base=50, gain=0.6)

# ================= OP (22-40) funk =================
BPM = 128.0
B = 60.0 / BPM
BAR = 4 * B
RIFF = [
    (0.0, 38), (0.75, 50), (1.0, 41), (1.5, 43), (2.0, 45), (2.5, 45),
    (3.0, 48), (3.75, 47),
    (4.0, 38), (4.75, 50), (5.0, 41), (5.5, 43), (6.0, 45), (6.5, 48),
    (7.0, 50), (7.5, 52),
]
LEAD = [
    (0.0,0.5,74),(0.5,0.5,72),(1.0,1.0,69),(2.0,0.75,72),(2.75,0.25,74),(3.0,1.0,76),
    (4.0,0.5,74),(4.5,0.5,72),(5.0,1.0,69),(6.0,1.5,67),(7.5,0.5,69),
    (8.0,0.5,74),(8.5,0.5,77),(9.0,1.0,76),(10.0,0.75,72),(10.75,0.25,74),(11.0,1.0,69),
    (12.0,0.5,74),(12.5,0.5,72),(13.0,1.0,69),(14.0,1.0,65),(15.0,1.0,62),
    (16.0,1.5,74),(17.5,0.5,72),(18.0,1.0,69),(19.0,0.5,67),(19.5,0.5,69),(20.0,2.0,74),
    (22.0,0.5,76),(22.5,0.5,74),(23.0,0.5,72),(23.5,0.5,69),(24.0,0.75,67),(24.75,0.25,65),(25.0,3.0,62),
]
T_OP = EV["op_logo"]
for bar in range(9):
    tb = T_OP + bar * BAR
    if tb > T_OP + 17.6: break
    for b in range(4):
        t4 = tb + b * B
        kick(t4)
        if b in (1, 3): snare(t4)
        for h8 in np.arange(0, B, B / 2):
            hat(t4 + h8, 0.15 if h8 == 0 else 0.09)
    kick(tb + 3.5 * B, 0.65)
    for pos, m in RIFF:
        pluck(m, 0.28, "square", 0.32, 0.0, tb + pos * B)
for bo, bd, m in LEAD:
    t0 = T_OP + B + bo * B
    if t0 < T_OP + 17.7:
        pluck(m, bd * B * 0.9, "tri", 0.24, 0.25, t0)
        pluck(m + 12, bd * B * 0.9, "sine", 0.07, 0.4, t0)
brass_hit(T_OP + 0.05, [50, 62, 66, 69], 0.85)
for st, ms in zip(EV["op_cards"], [[62, 66, 69], [60, 64, 67], [65, 69, 72], [64, 68, 71]]):
    brass_hit(st + 0.0, ms, 0.45)
brass_hit(EV["op_group"] + 1.5, [57, 61, 64, 69], 0.5)
brass_hit(EV["op_finale"], [50, 62, 66, 69, 74], 1.0)
gong(EV["op_finale"], base=50, gain=0.7)

# ================= A-PART (40-130) sitcom groove =================
T_A = 40.0
for bar in range(int(90 / BAR)):
    tb = T_A + bar * BAR
    if tb > 129.6: break
    for b in range(4):
        t4 = tb + b * B
        kick(t4, 0.55)
        if b in (1, 3): hat(t4 + B / 2, 0.12)
        for h8 in np.arange(0, B, B / 2):
            hat(t4 + h8, 0.09 if h8 == 0 else 0.06)
    for pos, m in [(0.0, 38), (1.5, 41), (2.0, 45), (3.0, 43)]:
        pluck(m, 0.3, "tri", 0.24, 0.0, tb + pos * B)
    if bar % 4 in (1, 3):
        chord(tb, [62, 65, 69] if bar % 8 < 4 else [60, 64, 67], 1.6, "tri", 0.16)
# scene stings
brass_hit(EV["shadow_t"], [38, 44, 45, 46], 0.5, dur=1.4)      # horror cluster
rattle(EV["shadow_t"] + 2.55, 0.55)                            # "The landlord."
brass_hit(EV["flag_t"], [57, 61, 64, 69, 73], 0.7, dur=1.2)    # Xargothia anthem
sad_womp(EV["laugh_t"][1] + 0.6, 0.4)                          # treasury rejected
for lt in EV["laugh_t"][:4]:
    brass_hit(lt, [66, 70, 73], 0.4, dur=0.5)
    crowd_puff(lt, 0.5)

# ================= EYECATCH (130-135) =================
T_E = EV["eye_t"]
kick(T_E + 0.05, 0.8); pluck(50, 0.2, "square", 0.4, 0, T_E + 0.05)
kick(T_E + 0.45, 0.7); pluck(45, 0.2, "square", 0.4, 0, T_E + 0.45)
hat(T_E + 0.8, 0.5, 0.25)
for j, m in enumerate([74, 78, 81, 86]):
    t0 = T_E + 1.1 + j * 0.22
    pluck(m, 0.7, "sine", 0.30, -0.2 + j * 0.13, t0)
    pluck(m + 12, 0.5, "sine", 0.10, 0.3, t0)
chord(T_E + 2.6, [62, 66, 69, 74], 1.2, "tri", 0.5)

# ================= B-PART (135-225) =================
T_B = 135.0
sil0, sil1 = EV["payday_silence"]
for bar in range(int(90 / BAR)):
    tb = T_B + bar * BAR
    if tb > 224.6 or tb > sil0 - 0.4: break
    for b in range(4):
        t4 = tb + b * B
        kick(t4, 0.7)
        if b in (1, 3):
            snare(t4, 0.45)
            snare(t4 + B / 2, 0.22)
        for h8 in np.arange(0, B, B / 2):
            hat(t4 + h8, 0.13 if h8 == 0 else 0.08)
    kick(tb + 3.5 * B, 0.5)
    for pos, m in [(0.0, 40), (0.75, 47), (1.5, 43), (2.0, 45), (3.0, 47), (3.5, 48)]:
        pluck(m, 0.26, "square", 0.28, 0.0, tb + pos * B)
    if bar % 2 == 1:
        chord(tb, [57, 60, 64], 1.5, "tri", 0.15)
# war sting + review sad
brass_hit(EV["laugh_t"][4] * 0 + 165.0 + 0.0, [44, 45, 47, 48], 0.5, dur=1.3)
sad_womp(EV["review_t"], 0.45)
# PAYDAY choir then SILENCE
choir_pad(EV["payday_t"], [50, 57, 62, 66, 69], 5.0, 0.5)
# warm pad after silence
choir_pad(sil1, [45, 52, 57, 61], 6.0, 0.35)
for i, bt in enumerate(np.arange(sil1 + 2.0, sil1 + 12.0, B)):
    hat(bt, 0.10)
brass_hit(203.8, [55, 62, 66], 0.4)
# Obaa doom + collapse
brass_hit(EV["obaa_t"], [36, 37, 43, 44], 0.55, dur=2.0)
rattle(EV["obaa_t"] + 0.4, 0.6, 10)
gong(EV["collapse_t"], base=34, gain=0.8)
brass_hit(EV["collapse_t"] + 0.1, [31, 43], 0.6, dur=1.6)

# ================= END CARD (225-235.2) =================
T_F = EV["end_t"]
for tc, ms in [(T_F + 0.6, [50, 57, 62, 66]), (T_F + 2.6, [48, 55, 60, 64]),
               (T_F + 4.6, [46, 53, 58, 62])]:
    chord(tc, ms, 1.9, "tri", 0.36)
    pluck(ms[0] - 12, 0.6, "tri", 0.26, 0.0, tc)
brass_hit(228.3, [50, 57, 62], 0.4)
kick(233.6, 0.7); pluck(50, 0.15, "square", 0.32, 0, 233.6)
kick(233.95, 0.6); pluck(45, 0.15, "square", 0.32, 0, 233.95)
hat(234.3, 0.45, 0.3)
pluck(74, 0.9, "sine", 0.28, 0.2, 234.5)

# ================= silence window (payday beat) =================
s0, s1 = int(sil0 * SR), int(sil1 * SR)
fade = int(0.25 * SR)
if s1 > s0 + fade:
    ramp = np.ones(N)
    ramp[s0:s0 + fade] = np.linspace(1, 0, fade)
    ramp[s1 - fade:s1] = np.linspace(0, 1, fade)
    ramp[s0:s1] = 0.0
    mixL *= ramp; mixR *= ramp
    for tt in np.arange(s0 / SR + 0.4, s1 / SR - 0.2, 0.5):
        clock_tick(tt)

# ================= master =================
stereo = np.stack([mixL, mixR], axis=1)
stereo = np.tanh(stereo * 1.1) * 0.85
peak = np.max(np.abs(stereo)) or 1.0
stereo = stereo / peak * 0.88
pcm = (stereo * 32767).astype(np.int16)
out = os.path.join(ROOT, "score.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", out, f"{DUR:.1f}s peak={peak:.3f}")
