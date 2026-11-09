#!/usr/bin/env python3
"""DLPR Episode 2 FULL — line manifest, TTS batch generation, timeline builder.

「深淵のWi-Fiパスワード」— The Abyssal Wi-Fi Password.

Segment map (absolute, 30fps) — identical skeleton to Ep1:
  cold 0.0-22.0 (660f) | op 22.0-40.0 (540f)
  apart 40.0-130.0 (2700f) A1 0-525 | A2 525-1220 | A3 1220-1970 | A4 1970-2700
  eye 130.0-135.0 (150f) | bpart 135.0-225.0 (2700f)
       B1 0-750 | B2 750-1410 | B3 1410-2100 | B4 2100-2700
  end 225.0-236.6 (348f)
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(ROOT, "audio_clips")
os.makedirs(CLIPS, exist_ok=True)

VOICES = {
    "n": ("jam", 1.80),      # SENIOR the cat — deadpan narrator
    "x": ("luodo", 2.00),    # XARGOTH — grandiose
    "k": ("douji", 1.60),    # KENJI — stressed
    "m": ("xiaochen", 1.20), # TASTY MART manager
    "c": ("kazi", 1.60),     # customer
    "o": ("tongtong", 1.40), # landlord Obaa-san
}

# hard end (absolute sec) for each line's scene window
SCENE_ENDS = {
    "n01": 8.40, "x01": 13.55, "k01": 16.85, "x02": 18.65, "n02": 21.85,
    "n03": 35.30,
    "n04": 43.90, "n05": 46.30, "k02": 50.10, "x03": 54.90, "n06": 57.40,
    "n07": 59.90, "x04": 65.00, "k03": 68.50, "n08": 70.60, "x05": 72.90,
    "n09": 76.60,
    "n10": 82.80, "x06": 88.10, "k04": 91.30, "x07": 97.60, "n11": 100.70,
    "k05": 104.90,
    "n12": 107.90, "x08": 112.90, "k06": 116.00, "n13": 122.30, "x09": 127.10,
    "n14": 129.70,
    "n15": 138.50, "m01": 142.60, "x10": 148.80, "k08": 152.80, "n16": 156.30,
    "x11": 159.70,
    "n17": 164.00, "c01": 167.30, "x12": 171.30, "k09": 175.20, "n18": 179.10,
    "x13": 181.80,
    "m02": 186.30, "x14": 190.80, "n19": 194.70, "k10": 198.70, "n20": 204.00,
    "x15": 207.50, "k11": 209.80,
    "n21": 213.90, "o01": 219.10, "o02": 223.10, "x16": 225.00,
    "k12": 229.50, "x17": 232.70, "n22": 236.20,
}

LINES = [
    # ---- COLD OPEN (0-22) ------------------------------------------------
    ("n01", "n", 0.80, "Apartment 302. Saturday, six a.m. The demon lord rose for the most sacred of rituals: the router."),
    ("x01", "x", 8.60, "Kneel, small box of stars. Pour the abyss into my phone."),
    ("k01", "k", 13.90, "Red since Tuesday. That's the RENT light."),
    ("x02", "x", 17.00, "There is a light... for RENT?"),
    ("n02", "n", 18.95, "There is a light for everything. Except options."),
    # ---- OP (22-40) --------------------------------------------------------
    ("n03", "n", 31.80, "One crown. One debt. Zero bars."),
    # ---- A-PART (40-130) ---------------------------------------------------
    ("n04", "n", 40.60, "The plan had been simple. Sell the crown. Online."),
    ("n05", "n", 44.30, "The plan required... the internet."),
    ("k02", "k", 46.70, "Which is off. Because of the rent. Which is YOU."),
    ("x03", "x", 50.50, "Then the crown goes to auction. The reserve: two hundred thirty-eight thousand yen."),
    ("n06", "n", 55.30, "Priced at exactly the gap. It hurt."),
    # ---- A2: plan one — overwhelming force ----
    ("n07", "n", 58.20, "Plan one: overwhelming force."),
    ("x04", "x", 60.20, "Wake, machine. I am Xargoth the Unending. UNENDING. Think of your warranty."),
    ("k03", "k", 65.40, "It means you unplug it and plug it back in."),
    ("n08", "n", 68.90, "The ancient rite was performed."),
    ("x05", "x", 71.00, "It lives—"),
    ("n09", "n", 73.40, "It lived four seconds. Then it remembered the rent."),
    # ---- A3: plan two — the guessing abyss ----
    ("n10", "n", 81.30, "Plan two: the guessing abyss."),
    ("x06", "x", 82.90, "Every abyss has a name. Xargoth. XARGOTH. xargoth666..."),
    ("k04", "k", 88.50, "Her router. 'Obaa' plus numbers."),
    ("x07", "x", 91.70, "Then the abyss shall know: obaa1. obaa12. obaa123."),
    ("n11", "n", 98.00, "Attempt forty-one: declined. Politely."),
    ("k05", "k", 101.10, "Locked out. Thirty minutes. Raid boss."),
    # ---- A4: plan three — diplomacy ----
    ("n12", "n", 106.30, "Plan three: diplomacy."),
    ("x08", "x", 108.30, "I shall negotiate as equals. Myself. And the woman who owns the building."),
    ("k06", "k", 113.30, "Those are the same IOUs from March."),
    ("n13", "n", 119.40, "The door opened four centimeters. A note emerged."),
    ("x09", "x", 122.70, "'Wi-Fi resumes when rent does.' She RHYMED. She had this READY."),
    ("n14", "n", 127.50, "The war cabinet met for eleven seconds."),
    # ---- B-PART (135-225) ---------------------------------------------------
    ("n15", "n", 135.60, "Night shift. The last free Wi-Fi in the realm."),
    ("m01", "m", 139.00, "Password's on the receipt. Receipt comes with a purchase."),
    ("x10", "x", 143.20, "Name your price, gatekeeper. The crown of the Unending awaits the highest bidder. I require... one pudding."),
    ("k08", "k", 149.40, "The last pudding. Paid in couch coins."),
    ("n16", "n", 153.30, "The receipt said: obaa-zero-three-zero-two."),
    ("x11", "x", 156.80, "The abyss... was a pudding."),
    # ---- B2: the auction rises ----
    ("n17", "n", 160.80, "The listing went live. 'Cursed crown. Slightly weeping.'"),
    ("c01", "c", 164.60, "Is the weeping... a feature?"),
    ("x12", "x", 167.90, "The crown weeps only for the unworthy. You may proceed."),
    ("k09", "k", 171.90, "My lord, restock. The onigiri are unionizing."),
    ("n18", "n", 175.80, "By nine forty, the bid was one hundred fifty thousand."),
    ("x13", "x", 179.60, "WHO DARES WARM FOOD."),
    # ---- B3: microwave war + the snipe ----
    ("m02", "m", 182.60, "The microwave is essential equipment. No war on the microwave."),
    ("x14", "x", 187.00, "Then I shall wait. Like the tide. Like the dungeon."),
    ("n19", "n", 191.40, "At nine fifty-eight: two hundred thirty-eight thousand. Exact."),
    ("k10", "k", 195.30, "Sixty seconds. Don't breathe. Don't microwave anything."),
    ("n20", "n", 200.90, "The listing closed offline. Outbid by... obaa, god, seven-seven-seven."),
    ("x15", "x", 204.60, "...The crown was never about the money."),
    ("k11", "k", 208.00, "It was entirely about the money."),
    # ---- B4: the buyer ----
    ("n21", "n", 210.60, "At closing, the final customer arrived. She had already bought."),
    ("o01", "o", 214.30, "Two thirty-eight. Delivery: me. Crown stays on your head."),
    ("o02", "o", 219.50, "Interest: waived. This once."),
    ("x16", "x", 223.40, "Rent: cleared. Dignity: pending."),
    # ---- END CARD (225-236.6) ----------------------------------------------
    ("k12", "k", 226.20, "The password. IT WAS ON THE LEASE. Page nine. 'Amenities.'"),
    ("x17", "x", 230.00, "I know. I signed it."),
    ("n22", "n", 233.10, "Never locked against him. Only against the cat."),
]

FPS = 30
SEGS = [
    ("cold", 660), ("op", 540), ("apart", 2700),
    ("eye", 150), ("bpart", 2700), ("end", 348),
]
TOTAL_F = sum(n for _, n in SEGS)
TOTAL_S = TOTAL_F / FPS


RAW = os.path.join(CLIPS, "raw")
os.makedirs(RAW, exist_ok=True)
ATEMPO_CAP = 1.18


def gen_clip(lid, voice, speed, text):
    out = os.path.join(RAW, f"{lid}.wav")
    if os.path.exists(out) and os.path.getsize(out) > 4000:
        return out
    for attempt in range(5):
        r = subprocess.run(
            ["z-ai", "tts", "-i", text, "-o", out, "--voice", voice,
             "--speed", str(speed), "--format", "wav"],
            capture_output=True, text=True, timeout=180)
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 4000:
            time.sleep(3)
            return out
        wait = 45 + attempt * 30
        print(f"  retry {lid} in {wait}s ({(r.stderr or r.stdout).strip()[-70:]})", flush=True)
        time.sleep(wait)
    return None


def dur_of(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def fit_clip(lid, target_end, start):
    """If raw clip overflows its slot, time-compress it (atempo) to fit."""
    raw = os.path.join(RAW, f"{lid}.wav")
    out = os.path.join(CLIPS, f"{lid}.wav")
    avail = target_end - start - 0.10
    d = dur_of(raw)
    if d <= avail or avail <= 0.4:
        if os.path.exists(out):
            os.remove(out)
        os.link(raw, out) if not os.path.exists(out) else None
        return d, 1.0
    tempo = min(ATEMPO_CAP, d / avail)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw,
                    "-filter:a", f"atempo={tempo:.4f}", out], check=True)
    return dur_of(out), tempo


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    entries, missing = [], []
    for lid, vk, start, text in LINES:
        if only and lid not in only:
            continue
        voice, speed = VOICES[vk]
        if gen_clip(lid, voice, speed, text) is None:
            missing.append(lid)
            continue
        d, tempo = fit_clip(lid, SCENE_ENDS[lid], start)
        entries.append({"id": lid, "voice": vk, "start": start, "dur": round(d, 3),
                        "end": round(start + d, 3), "tempo": round(tempo, 3), "text": text})
        tag = f" tempo={tempo:.2f}" if tempo > 1.001 else ""
        print(f"{lid} [{vk}] {start:7.2f} + {d:5.2f} = {start+d:7.2f}{tag}  {text[:44]}", flush=True)

    # sequential de-overlap inside each scene: push late, then fit again
    for i in range(1, len(entries)):
        prev, cur = entries[i - 1], entries[i]
        if cur["start"] < prev["end"] + 0.15 and SCENE_ENDS[prev["id"]] <= SCENE_ENDS[cur["id"]]:
            shift = prev["end"] + 0.15 - cur["start"]
            raw = os.path.join(RAW, f"{cur['id']}.wav")
            new_start = cur["start"] + shift
            d, tempo = fit_clip(cur["id"], SCENE_ENDS[cur["id"]], new_start)
            cur.update({"start": round(new_start, 3), "dur": round(d, 3),
                        "end": round(new_start + d, 3), "tempo": round(tempo, 3), "shift": round(shift, 2)})
            print(f"  >> shifted {cur['id']} +{shift:.2f}s -> {new_start:.2f}", flush=True)

    if missing:
        print(f"MISSING CLIPS: {missing} — re-run to resume")
    if not entries:
        return
    total_end = max(e["end"] for e in entries)
    print(f"last line ends at {total_end:.2f}s (video {TOTAL_S:.1f}s)")

    offs, acc = {}, 0.0
    for name, nf in SEGS:
        offs[name] = round(acc, 3)
        acc += nf / FPS

    E = {e["id"]: e for e in entries}

    def lend(lid):
        return E[lid]["end"] if lid in E else SCENE_ENDS.get(lid, 0)

    laugh_t = [round(lend("n06") + 0.30, 2), round(lend("n09") + 0.25, 2),
               round(lend("n11") + 0.30, 2), round(lend("x09") + 0.25, 2),
               round(lend("x11") + 0.25, 2), round(lend("k11") + 0.25, 2)]
    freeze = round(max(18.0, E["n02"]["start"] - 0.25), 2) if "n02" in E else 18.70
    snap = round(max(16.5, E["x02"]["start"] - 0.12), 2) if "x02" in E else 16.88

    timeline = {
        "fps": FPS, "total_frames": TOTAL_F, "total_sec": TOTAL_S,
        "segs": [{"name": n, "frames": nf, "start": round(a, 3),
                  "end": round(a + nf / FPS, 3)} for (n, nf), a in
                 zip(SEGS, [offs[x[0]] for x in SEGS])],
        "lines": sorted(entries, key=lambda e: e["start"]),
        "events": {
            "freeze_f": int(round(freeze * FPS)), "freeze_t": freeze,
            "snap_t": snap, "don_k1": round(E["k01"]["start"] + 0.1, 2) if "k01" in E else 14.0,
            "op_logo": offs["op"],
            "op_cards": [offs["op"] + 40 / FPS, offs["op"] + 120 / FPS,
                         offs["op"] + 200 / FPS, offs["op"] + 280 / FPS],
            "op_group": offs["op"] + 280 / FPS, "op_finale": offs["op"] + 400 / FPS,
            "eye_t": offs["eye"],
            "laugh_t": laugh_t,
            "brute_t": round(E["x06"]["start"], 2) if "x06" in E else 83.3,
            "plug_t": round(E["k03"]["start"], 2) if "k03" in E else 65.4,
            "hope_t": round(E["x05"]["start"], 2) if "x05" in E else 71.0,
            "die_t": round(E["n09"]["start"], 2) if "n09" in E else 73.4,
            "shadow_t": round(E["n13"]["start"] - 0.9, 2) if "n13" in E else 118.5,
            "live_t": round(E["n17"]["start"], 2) if "n17" in E else 160.8,
            "micro_t": round(E["x13"]["start"] - 0.1, 2) if "x13" in E else 179.5,
            "bid_t": round(E["n19"]["start"], 2) if "n19" in E else 191.4,
            "snipe_t": round(E["k10"]["end"] + 0.2, 2) if "k10" in E else 198.9,
            "payday_silence": [round(E["k10"]["end"] + 0.5, 2) if "k10" in E else 199.2,
                               round(E["n20"]["start"] - 0.2, 2) if "n20" in E else 200.7],
            "obaa_t": round(E["n21"]["start"] + 0.2, 2) if "n21" in E else 210.8,
            "deal_t": round(E["o01"]["end"], 2) if "o01" in E else 219.1,
            "end_t": offs["end"],
        },
    }
    out = os.path.join(ROOT, "timeline.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(timeline, fh, ensure_ascii=False, indent=1)
    print("wrote", out, f"total {TOTAL_S:.1f}s / {TOTAL_F}f")
    if missing:
        sys.exit(3)


if __name__ == "__main__":
    main()
