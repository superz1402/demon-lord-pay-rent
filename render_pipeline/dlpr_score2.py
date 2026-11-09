#!/usr/bin/env python3
"""DLPR Episode 2 FULL — 236.6s stereo score + SFX, driven by timeline.json.

Sections (absolute seconds):
  cold 0-22     sparse pizzicato + gongs, LED dread pings, horror cluster,
                snap shimmer, freeze scratch, smash
  op 22-40      funk @128, card stingers, group lift, finale fanfare
  apart 40-130  sitcom groove, plan stings, zap, hope shimmer, sad-womp,
                brute-force beeps, door horror + keyring, gong, laugh stabs
  eye 130-135   ba-dum-tss + bell arpeggio
  bpart 135-225 groove -> AUCTION theme (live_t), microwave war sting,
                countdown ticks, Wi-Fi drop, SILENCE beat, laugh stabs,
                obaa doom + keyring, deal gong + warm choir
  end 225-236.6 outro chords, lease-reveal sting, final tag
Writes score.wav (44.1k stereo).
"""
import json, os
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
rng = np.random.default_rng(11)

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
    for i in range(n_ding):
        tt = t0 + i * 0.055 + rng.uniform(0, 0.02)
        f = 2600 + rng.uniform(-400, 700)
        n = int(0.09 * SR)
        t = np.arange(n) / SR
        sig = np.sin(2 * np.pi * f * t) * np.exp(-t * 55) * 0.8
        sig += np.sin(2 * np.pi * f * 2.7 * t) * np.exp(-t * 80) * 0.3
        add(sig, tt, rng.uniform(-0.4, 0.4), gain)

def crowd_puff(t0, gain=0.4):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    noise = np.random.default_rng(int(t0 * 31) % (2**31)).normal(0, 1, n)
    noise = np.diff(noise, prepend=0)
    band = noise * np.exp(-((t - 0.22) ** 2) / 0.02)
    add(band * env(n, a=0.05, d=0.1, s=0.6, r=0.25), t0, 0.0, gain)

def clock_tick(t0, gain=0.25):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 120)
    add(sig, t0, 0.2, gain)

def sad_womp(t0, gain=0.5):
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

def led_ping(t0, gain=0.22):
    """Router LED dread ping — sonar blip."""
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f = 660 * np.exp(-t * 3) + 330
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    add(sig, t0, -0.2, gain)
    add(sig * 0.5, t0 + 0.18, 0.3, gain * 0.5)

def zap_fx(t0, gain=0.6):
    """Static shock zap."""
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    r2 = np.random.default_rng(int(t0 * 977) % (2**31))
    sig = r2.normal(0, 1, n) * np.exp(-t * 26)
    f = 800 * np.exp(-t * 14) + 160
    sig += 0.7 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 18)
    add(sig, t0, 0.0, gain)

def buzz_wrong(t0, gain=0.4):
    """Wrong-password buzzer."""
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    sig = np.sign(np.sin(2 * np.pi * 138 * t)) * 0.6 + np.sign(np.sin(2 * np.pi * 98 * t)) * 0.4
    sig *= env(n, a=0.004, d=0.05, s=0.7, r=0.05)
    add(sig, t0, 0.0, gain)

def pitch_drop(t0, gain=0.7):
    """Wi-Fi dying — descending saw."""
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 420 * np.exp(-t * 2.6) + 60
    sig = tone(1, 0.9, "saw")
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) * 0.6 + np.sign(np.sin(ph)) * 0.4
    sig *= env(n, a=0.01, d=0.4, s=0.5, r=0.3)
    add(sig, t0, 0.0, gain)

def hope_shimmer(t0, gain=0.4):
    for j, m in enumerate([72, 76, 79, 84, 88]):
        pluck(m, 0.5, "sine", gain * 0.6, -0.3 + j * 0.15, t0 + j * 0.11)

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
for bt in np.arange(3.2, 12.4, 1.6):     # red LED dread pings
    led_ping(bt, 0.16)
brass_hit(12.3, [38, 44, 45, 46], 0.5, dur=1.4)   # the rent light
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
# plan stings
brass_hit(EV["laugh_t"][0] * 0 + 58.2, [57, 61, 64, 69], 0.5, dur=1.0)   # plan one
zap_fx(EV["plug_t"], 0.65)
hope_shimmer(EV["hope_t"], 0.4)
sad_womp(EV["die_t"] + 0.1, 0.45)
for i in range(7):                                   # brute-force beeps
    buzz_wrong(EV["brute_t"] + 0.9 + i * 1.15, 0.30)
sad_womp(EV["laugh_t"][2] + 0.5, 0.30)               # politely declined
brass_hit(EV["shadow_t"], [38, 44, 45, 46], 0.5, dur=1.4)  # the door
rattle(EV["shadow_t"] + 2.2, 0.55)                   # keyring
gong(EV["laugh_t"][3] + 1.9, base=40, gain=0.45)     # eleven seconds
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
T_LIVE = EV["live_t"]
# groove until the listing goes live
for bar in range(int(90 / BAR)):
    tb = T_B + bar * BAR
    if tb > T_LIVE - 0.4: break
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
# AUCTION theme — tense minor pizzicato from live_t to sil0
T_AU = T_LIVE
while T_AU < sil0 - 0.4:
    bar_i = int((T_AU - T_LIVE) / BAR)
    for b in range(4):
        t4 = T_AU + b * B
        kick(t4, 0.45)
        hat(t4 + B / 2, 0.10)
    for pos, m in [(0.0, 40), (0.5, 43), (1.0, 47), (1.5, 46), (2.0, 40), (2.5, 43),
                   (3.0, 48), (3.5, 47)]:
        pluck(m, 0.18, "square", 0.22, 0.0, T_AU + pos * B)
    if bar_i % 2 == 0:
        chord(T_AU, [53, 56, 60], 1.4, "tri", 0.13)
    else:
        chord(T_AU, [52, 55, 59], 1.4, "tri", 0.13)
    T_AU += BAR
brass_hit(EV["micro_t"], [44, 45, 47, 48], 0.55, dur=1.3)   # microwave war
zap_fx(EV["micro_t"] + 0.35, 0.5)
for bt in np.arange(EV["bid_t"], EV["snipe_t"], 0.5):       # countdown ticks
    clock_tick(bt, 0.30)
for bt in np.arange(EV["bid_t"], EV["snipe_t"], 1.0):       # heartbeat
    kick(bt, 0.4)
scratch(EV["snipe_t"], 0.5, 0.8)                            # Wi-Fi drop
pitch_drop(EV["snipe_t"] + 0.1, 0.6)
# warm pad after silence (the deal is coming)
choir_pad(sil1 + 0.3, [45, 52, 57, 61], 5.0, 0.30)
for lt in EV["laugh_t"][4:6]:
    brass_hit(lt, [66, 70, 73], 0.4, dur=0.5)
    crowd_puff(lt, 0.5)
# Obaa doom + the deal
brass_hit(EV["obaa_t"], [36, 37, 43, 44], 0.55, dur=2.0)
rattle(EV["obaa_t"] + 0.4, 0.6, 10)
gong(EV["deal_t"], base=34, gain=0.8)
choir_pad(EV["deal_t"] + 0.3, [50, 57, 62, 66, 69], 4.5, 0.42)

# ================= END CARD (225-236.6) =================
T_F = EV["end_t"]
for tc, ms in [(T_F + 0.6, [50, 57, 62, 66]), (T_F + 2.6, [48, 55, 60, 64]),
               (T_F + 4.6, [46, 53, 58, 62])]:
    chord(tc, ms, 1.9, "tri", 0.36)
    pluck(ms[0] - 12, 0.6, "tri", 0.26, 0.0, tc)
brass_hit(226.3, [50, 57, 62], 0.5)                         # IT WAS ON THE LEASE
gong(226.35, base=44, gain=0.4)
kick(233.6, 0.7); pluck(50, 0.15, "square", 0.32, 0, 233.6)
kick(233.95, 0.6); pluck(45, 0.15, "square", 0.32, 0, 233.95)
hat(234.3, 0.45, 0.3)
pluck(74, 0.9, "sine", 0.28, 0.2, 234.5)

# ================= silence window (auction-ended beat) =================
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
