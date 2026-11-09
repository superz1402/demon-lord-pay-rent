#!/usr/bin/env python3
"""DLPR Episode 1 FULL — line manifest, TTS batch generation, timeline builder.

Generates every narration/dialogue clip via the z-ai TTS CLI, measures real
durations, and emits timeline.json — the single source of truth consumed by
the score generator, the renderer and the mixer.

Segment map (absolute, 30fps):
  cold 0.0-22.0 (660f) | op 22.0-40.0 (540f)
  apart 40.0-130.0 (2700f) A1 0-525 | A2 525-1220 | A3 1220-1970 | A4 1970-2700
  eye 130.0-135.0 (150f) | bpart 135.0-225.0 (2700f)
       B1 0-750 | B2 750-1410 | B3 1410-2100 | B4 2100-2700
  end 225.0-235.2 (306f)
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(ROOT, "audio_clips")
os.makedirs(CLIPS, exist_ok=True)

VOICES = {
    "n": ("jam", 1.80),      # SENIOR the cat — deadpan narrator (jam speaks VERY slow)
    "x": ("luodo", 2.00),    # XARGOTH — grandiose (luodo even slower)
    "k": ("douji", 1.60),    # KENJI — stressed
    "m": ("xiaochen", 1.20), # TASTY MART manager
    "c": ("kazi", 1.60),     # customer
    "o": ("tongtong", 1.40), # landlord Obaa-san
}

# hard end (absolute sec) for each line's scene window (fit-to-slot target)
SCENE_ENDS = {
    "n01": 9.2, "x01": 13.9, "k01": 16.9, "x02": 18.7, "n02": 22.0,
    "n03": 35.3,
    "n04": 43.2, "n05": 44.7, "k02": 48.5, "x03": 51.9, "x04": 54.8,
    "n06": 57.7, "n07": 60.4, "x05": 66.2, "k03": 70.0, "x06": 72.2,
    "k04": 77.1, "n08": 81.2,
    "n09": 83.9, "x07": 90.4, "n10": 94.1, "k05": 98.4, "n11": 105.6,
    "n12": 108.9, "k06": 113.1, "x08": 118.2, "m01": 120.5, "x09": 125.4,
    "n13": 129.8,
    "n14": 140.1, "x10": 152.9, "n15": 160.0,
    "c01": 164.9, "x11": 170.3, "k07": 173.5, "x12": 177.9, "n16": 182.0,
    "n17": 190.7, "x13": 195.5, "n18": 198.9, "k08": 203.7, "x14": 209.9,
    "n19": 213.6, "x15": 217.3, "o01": 223.1, "x16": 225.4,
    "x17": 231.9, "k09": 235.2,
}

LINES = [
    # ---- COLD OPEN (0-22) ------------------------------------------------
    ("n01", "n", 0.80, "Apartment 302. Friday night. A demon lord, one hundred and eight worlds conquered... three months behind on rent."),
    ("x01", "x", 9.30, "One hundred and eight worlds conquered. A landlord? The logistics... elude me."),
    ("k01", "k", 14.10, "Xargoth. Rent day. THREE. MONTHS."),
    ("x02", "x", 17.00, "Behold. Economics."),
    ("n02", "n", 18.95, "Yep. Two hundred and eighty four thousand yen behind on rent. Same."),
    # ---- OP (22-40) --------------------------------------------------------
    ("n03", "n", 31.80, "Three months behind. One cat. Unbothered."),
    # ---- A-PART (40-130) ---------------------------------------------------
    ("n04", "n", 40.60, "Then, under the door... a shadow."),
    ("n05", "n", 43.30, "The landlord."),
    ("k02", "k", 44.80, "He turned the rent envelope into confetti. Again."),
    ("x03", "x", 48.60, "Paper is temporary. The crown is forever."),
    ("x04", "x", 52.00, "The small one will protect me."),
    ("n06", "n", 54.90, "I could fix this. I choose not to."),
    ("n07", "n", 57.90, "Excuse number one: currency."),
    ("x05", "x", 60.50, "Behold! The treasury of the abyss!"),
    ("k03", "k", 66.30, "This is three thousand points at Tasty Mart."),
    ("x06", "x", 70.10, "A treasury."),
    ("k04", "k", 74.00, "Points. At. Tasty. Mart."),
    ("n08", "n", 77.20, "The treasury was not accepted."),
    ("n09", "n", 81.30, "Excuse number two: diplomacy."),
    ("x07", "x", 84.00, "I hereby declare this apartment sovereign territory! The nation of Xargothia!"),
    ("n10", "n", 90.50, "Treaties require signatures. I have marked mine."),
    ("k05", "k", 94.20, "The cat just contested your border."),
    ("n11", "n", 98.50, "The nation of Xargothia fell in eleven seconds."),
    ("n12", "n", 106.30, "Excuse number three: employment."),
    ("k06", "k", 109.00, "Tasty Mart is hiring. Interview. Tuesday. Please."),
    ("x08", "x", 113.20, "Under experience: one hundred and eight worlds."),
    ("m01", "m", 118.30, "Can you start Tuesday?"),
    ("x09", "x", 120.60, "He kneels first... this shop kneels first..."),
    ("n13", "n", 125.50, "He was hired before the tear hit the floor."),
    # ---- B-PART (135-225) ---------------------------------------------------
    ("n14", "n", 135.60, "Night one. The store had never known such efficiency."),
    ("x10", "x", 140.20, "Formations! Onigiri at the front. The pudding holds the line."),
    ("n15", "n", 153.00, "Sales rose nine hundred percent. Morale fell to zero."),
    ("c01", "c", 160.60, "Excuse me. Where is the limited edition pudding?"),
    ("x11", "x", 165.00, "You dare address the Demon Lord of the register?"),
    ("k07", "k", 170.40, "THE CUSTOMER IS AN ALLY, NOT A GOBLIN!"),
    ("x12", "x", 173.60, "Then the ally shall know my wrath."),
    ("n16", "n", 178.00, "He declared war on a customer. The customer left a one star review."),
    ("n17", "n", 183.00, "Payday. Forty six thousand yen. In an envelope."),
    ("x13", "x", 190.80, "...So this is what the peasants feel."),
    ("n18", "n", 195.60, "Character growth. Disgusting."),
    ("k08", "k", 199.00, "You did it. That's actually rent money. For one month."),
    ("x14", "x", 203.80, "Then the realm shall have... a second shift."),
    ("n19", "n", 210.40, "And so... the first wages of the demon lord."),
    ("x15", "x", 213.70, "Landlord. For the honor of the crown."),
    ("o01", "o", 217.40, "Three months is two hundred eighty four thousand, little king."),
    ("x16", "x", 223.20, "...I have conquered one hundred and eight worlds."),
    # ---- END CARD (225-235.2) ----------------------------------------------
    ("x17", "x", 228.20, "The router... shall kneel."),
    ("k09", "k", 232.00, "It's written on the lease. WHERE ARE MY KEYS."),
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

    laugh_t = [round(lend("n06") + 0.30, 2), round(lend("x06") + 0.25, 2),
               round(lend("n11") + 0.30, 2), round(lend("n13") + 0.30, 2),
               round(lend("n18") + 0.30, 2)]
    freeze = round(max(18.0, E["n02"]["start"] - 0.25), 2) if "n02" in E else 18.75
    snap = round(max(16.5, E["x02"]["start"] - 0.12), 2) if "x02" in E else 16.9
    obaa = round(E["o01"]["start"] - 0.3, 2) if "o01" in E else 217.1
    silence0 = round(lend("n17") + 0.1, 2)
    silence1 = round(E["x13"]["start"] - 0.1, 2) if "x13" in E else 190.5

    timeline = {
        "fps": FPS, "total_frames": TOTAL_F, "total_sec": TOTAL_S,
        "segs": [{"name": n, "frames": nf, "start": round(a, 3),
                  "end": round(a + nf / FPS, 3)} for (n, nf), a in
                 zip(SEGS, [offs[x[0]] for x in SEGS])],
        "lines": sorted(entries, key=lambda e: e["start"]),
        "events": {
            "freeze_f": int(round(freeze * FPS)), "freeze_t": freeze,
            "snap_t": snap, "don_k1": round(E["k01"]["start"] + 0.1, 2) if "k01" in E else 14.2,
            "op_logo": offs["op"],
            "op_cards": [offs["op"] + 40 / FPS, offs["op"] + 120 / FPS,
                         offs["op"] + 200 / FPS, offs["op"] + 280 / FPS],
            "op_group": offs["op"] + 280 / FPS, "op_finale": offs["op"] + 400 / FPS,
            "eye_t": offs["eye"],
            "laugh_t": laugh_t, "shadow_t": round(E["n04"]["start"], 2) if "n04" in E else 40.6,
            "flag_t": round(E["x07"]["start"], 2) if "x07" in E else 84.0,
            "review_t": round(lend("n16") - 0.8, 2),
            "payday_t": round(E["n17"]["start"], 2) if "n17" in E else 183.0,
            "payday_silence": [silence0, silence1],
            "obaa_t": obaa, "collapse_t": round(E["o01"]["end"], 2) if "o01" in E else 223.0,
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
