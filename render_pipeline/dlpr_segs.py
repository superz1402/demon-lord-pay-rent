#!/usr/bin/env python3
"""DLPR Ep1 FULL — segment renderers (cold / op / apart / eye / bpart / end).

Each seg_*(g) takes the ABSOLUTE frame index and returns a 1280x720 RGB frame.
All dialogue windows come from timeline.json via dlpr_common.subtitle().
"""
import math
from PIL import Image, ImageDraw
from dlpr_common import (
    TL, FPS, EVENTS, W, H, DW, DH, K,
    INK, CREAM, PAPER, WALL, WALL_D, FLOOR, LAMP, WINC, XSKIN, XSKIN_D,
    XCAPE, XCAPE_D, XCAPE_L, XHAIR, XHAIR_L, CROWN, KHOOD, KHOOD_D, KHAIR,
    KSKIN, KSKIN_D, CFUR, CFUR_D, CPATCH, HALO, ACCENT, FIRE, WHITE, REDC,
    SOFA, SOFA2, SOFA3, TABLE, TABLE2, CURT, LAUGHY, SKYB, SKYB2,
    TM_WALL, TM_FLOOR, TM_GREEN, TM_RED, LED_G, LED_R, GOLD,
    blend, clamp, prog, lerp, ease_out, ease_io, pop, shake,
    txt, txt_shadow, F, speedlines, menace, don, laugh, flash, cam_apply,
    subtitle, talking, line_window,
    xargoth2, kenji2, cat2, obaa2, minor_person,
    apartment2, tastymart2, chest, points_card, flag_x, map_x, review_card,
    onigiri, envelope_glow, vignette, draw_wipe,
)

E = EVENTS
S = {s["name"]: s for s in TL["segs"]}
OFF = {k2: S[k2]["start"] for k2 in S}
OFF_F = {k2: S[k2]["start"] * FPS for k2 in S}

SPK = {"x": (XCAPE, "XARGOTH"), "k": (KHOOD, "KENJI"),
       "n": ((212,180,40), "SENIOR (THE CAT)"), "m": ((60,160,90), "MANAGER"),
       "c": ((220,130,60), "CUSTOMER"), "o": ((190,80,110), "OBAA-SAN")}

# text lookup
TXT = {L["id"]: L["text"] for L in TL["lines"]}

JP = {
 "x01": "世界108を征服したが…家主は無理だ",
 "k01": "家賃の日だ！三ヶ月分！",
 "x02": "見よ、経済だ",
 "n02": "ここで問題の魔王",
 "n03": "三月滞納、一猫余裕",
 "k02": "封筒が紙吹雪にされた",
 "x03": "紙は朽ちる、王冠は不滅",
 "x04": "小さな守護者よ、頼む",
 "n06": "直せる。しないだけだ",
 "x05": "深淵の宝物庫だ！",
 "k03": "タスティーマートの3000ポイントだ",
 "x06": "宝物庫だ",
 "x07": "ここはザルゴス帝国領だ！",
 "n10": "条約には署名が必要だ",
 "k05": "猫が国境を主張した",
 "m01": "火曜日から来られる？",
 "x09": "土下座した…この店は土下座した…",
 "n13": "涙が地面に着く前に採用された",
 "x10": "陣形！おにぎりは最前線だ",
 "n15": "売上900%アップ、士気はゼロ",
 "x11": "レジの魔王に敬意を払え",
 "k07": "客は味方だ！ゴブリンじゃない！",
 "x12": "ならば味方に我が怒りを知らしめよう",
 "x13": "これが…庶民の気持ちか",
 "n18": "人間的成長。時代遅れだ",
 "k08": "やったな。一ヶ月分の家賃だ",
 "o01": "三ヶ月で28万4千円だよ、小さな王様",
 "x16": "…我は108の世界を征服した",
}


def banner(d, g, t0, num, word, dur=55):
    t = g - t0
    if t < 0 or t > dur: return
    s = 0.7 + 0.3 * pop(min(1, t / 8))
    cx, cy = 330 * K, 210 * K
    w2, h2 = 430 * s * K, 150 * s * K
    d.rounded_rectangle([cx - w2 + 14, cy - h2 + 14, cx + w2 + 14, cy + h2 + 14], 18, fill=INK)
    d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], 18, fill=LAUGHY, outline=INK, width=8)
    d.polygon([(cx - w2, cy - h2), (cx - w2 + 60, cy - h2), (cx - w2, cy - h2 + 60)], fill=ACCENT)
    txt(d, (cx, cy - 38 * s * K), num, F(64 * s * K), INK, anchor="mm")
    txt(d, (cx, cy + 48 * s * K), word, F(52 * s * K), ACCENT, anchor="mm")


def dust(d, f, t0, x, y, n=8, dur=22):
    t = f - t0
    if t < 0 or t > dur: return
    tt = t / dur
    for i in range(n):
        a = math.radians(i * (360 / n) + 15)
        r = ease_out(tt) * (40 + (i % 3) * 30)
        r0 = 6 + tt * 26
        d.ellipse([x + math.cos(a) * r - r0, y - r0 * 0.6, x + math.cos(a) * r + r0, y + r0 * 0.6],
                  fill=blend(CREAM, INK, 0.15), outline=blend(CREAM, INK, 0.5 - tt))


def confetti_iou(d, f, t0, x, y, dur=60):
    t = f - t0
    if t < 0 or t > dur: return
    tt = t / dur
    for i in range(14):
        ang = (i / 14) * math.pi * 2
        r = ease_out(tt) * (140 + (i % 4) * 55)
        ex = x + math.cos(ang) * r; ey = y + math.sin(ang) * r * 0.7
        col = FIRE if i % 3 == 0 else PAPER
        d.rectangle([ex - 22, ey - 14, ex + 22, ey + 14],
                    fill=blend(CREAM, col, 1 - tt), outline=blend(CREAM, INK, 1 - tt))
        if tt < 0.5:
            txt(d, (ex, ey - 8), "IOU", F(16), INK, anchor="mm")


# ============================ COLD OPEN ============================
def seg_cold(g):
    lf = g - OFF_F["cold"]
    img = Image.new("RGB", (DW, DH), WALL)
    d = ImageDraw.Draw(img)
    frozen = g >= E["freeze_f"]
    fz = E["freeze_f"] if frozen else g
    drift = lerp(120, 0, prog(lf, 0, 60))

    xarX, xarY = 450 + drift, 470
    kenjiX = lerp(2400, 1520, ease_out(prog(lf, 413, 433)))
    if lf >= 540:  # flees screaming from the IOU confetti
        kenjiX = lerp(1520, 2500, ease_io(prog(lf, 540, 596)))
    punch = 1 + 0.12 * math.sin(math.pi * prog(lf, 420, 440))

    apartment2(d, g, base=img)

    # Xargoth on his sofa-throne
    pose = "phone" if lf >= 200 else "idle"
    xargoth2(d, fz, xarX, xarY, 1.05,
             emotion=("menace" if lf < 270 else ("panic" if lf >= 524 else "smug")),
             talking=talking("x", g), pose=pose)
    if 60 <= lf < 275:
        menace(d, fz, 620 + drift, 300, ["ゴ", "ゴ", "ゴ"], CREAM, WALL)

    # Kenji with the envelope
    kenji2(d, fz, kenjiX + drift, 610, punch, panic=True,
           talking=talking("k", g), prop=("env" if lf < 519 else "none"))
    if 415 <= lf < 445:
        speedlines(d, fz, blend(WALL, WHITE, 0.35), 0.5, cx=1400, cy=500)
    if lf >= 520 and lf < 524:  # snap pose flash
        xargoth2(d, fz, xarX, xarY, 1.05, emotion="smug", pose="snap")

    # THE CAT on the kotatsu
    cat2(d, fz, 1420 + drift, 560, 1.12, pose=("sit" if frozen else "loaf"),
         sparkle=frozen)

    # snap → IOU confetti + チッ
    snap_t = E["snap_t"] * FPS
    if g >= snap_t:
        confetti_iou(d, g, snap_t, 1200 + drift, 430)
    if snap_t <= g < snap_t + 22:
        txt(d, (1200 + drift, 380), "チッ", F(54, True, True), FIRE,
            anchor="mm", stroke=6, sfill=INK)

    # freeze-frame stickers
    if frozen:
        txt(d, (1500 + drift, 330), "RECORD SCRATCH ♪", F(40), CREAM,
            anchor="mm", stroke=5, sfill=INK)
        menace(d, fz, 1290 + drift, 430, ["ピ", "ク"], CREAM, WALL, size=56)

    # camera: drift → push → punch-shake → zoom to cat
    sx, sy = (shake(lf, 6) if 424 <= lf < 436 else (0, 0))
    push = prog(lf, 279, 413)
    cam_x = lerp(0, -60, ease_out(push)) + sx
    cam_s = lerp(1.0, 1.08, ease_out(push))
    zt = prog(g, E["freeze_f"] - 20, E["freeze_f"])
    ze = ease_out(zt)
    cam_x = lerp(cam_x, -920, ze); cam_y = lerp(0, 120, ze); cam_s = lerp(cam_s, 2.1, ze)
    frame = cam_apply(img, cam_x, cam_y, cam_s)

    dd = ImageDraw.Draw(frame)
    # COLD OPEN chip
    if lf < 60:
        dd.rounded_rectangle([32 * K, 32 * K, 330 * K, 86 * K], 10 * K, fill=INK)
        txt(dd, (50 * K, 42 * K), "COLD OPEN", F(34 * K), CREAM)
    if frozen:
        frame = vignette(frame, 0.45)
        dd = ImageDraw.Draw(frame)
    laugh(dd, g, int(E["laugh_t"][0] * FPS) - 16, K, 26)  # A1 laugh lands early on cold? no-op if t<0
    laugh(dd, g, 470, K, 24)
    laugh(dd, g, 560, K, 22)
    don(dd, g, 426, 1460, 330, K)
    sub_frame(g, dd, ["n01", "x01", "k01", "x02", "n02"])
    dd2 = frame
    # smash flash + title
    if g >= E["freeze_f"] + 74:
        dd2 = flash(frame, g, E["freeze_f"] + 74, 6)
        dd = ImageDraw.Draw(dd2)
        dd.rectangle([0, 0, W, H], fill=CREAM)
        speedlines(dd, g, blend(CREAM, INK, 0.15), 0.3, cx=W / 2, cy=H / 2, k=K)
        sc = 0.7 + 0.3 * pop(min(1, (g - E["freeze_f"] - 78) / 9))
        txt(dd, (W / 2, H / 2 - 10), "魔王、家賃を払え！", F(84 * sc, True, True),
            ACCENT, anchor="mm", stroke=7, sfill=INK)
        txt(dd, (W / 2, H / 2 + 90), "EPISODE 1 — THE RENT MUST FLOW", F(30 * sc),
            INK, anchor="mm")
        don(dd, g, E["freeze_f"] + 80, 960 * K, 540 * K, K)
    return dd2


def sub_frame(g, dd, lids):
    for lid in lids:
        color, name = SPK[lid[:1]]
        subtitle(dd, g, lid, name, color, TXT[lid], jp=JP.get(lid), cat=(lid[:1] == "n"))


# ============================ OP ============================
def card_bg(d, f, color, color2, word):
    d.rectangle([0, 0, DW, DH], fill=color)
    shift = (f * 3) % 160
    for x0 in range(-500, 2500, 160):
        d.polygon([(x0 + shift, -100), (x0 + shift + 60, -100),
                   (x0 + shift - 240, 1180), (x0 + shift - 300, 1180)],
                  fill=blend(color, color2, 0.55))
    txt(d, (960, 540), word, F(620, True, True), blend(color, INK, 0.12), anchor="mm")
    speedlines(d, f, blend(color, WHITE, 0.5), 0.16)


def name_tag(d, f, t0, jp, en, tag, color, right=False):
    if f < t0: return
    sc = 0.7 + 0.3 * pop(min(1, (f - t0) / 9))
    bw, bh = 820, 220
    bx = 150 if not right else DW - 150 - bw
    cx, cy = bx + bw / 2, 830
    wp, hp = bw * sc, bh * sc
    d.rounded_rectangle([cx - wp / 2 + 14, cy - hp / 2 + 14, cx + wp / 2 + 14, cy + hp / 2 + 14],
                        18, fill=INK)
    d.rounded_rectangle([cx - wp / 2, cy - hp / 2, cx + wp / 2, cy + hp / 2], 18,
                        fill=CREAM, outline=INK, width=8)
    s = min(1, sc)
    txt(d, (cx - wp / 2 + 40, cy - hp / 2 + 6), jp, F(84 * s, True, True), INK)
    txt(d, (cx - wp / 2 + 40, cy - hp / 2 + 102), en, F(36 * s), color)
    txt(d, (cx - wp / 2 + 40, cy - hp / 2 + 152), tag, F(26 * s, False), blend(CREAM, INK, 0.72))


def seg_op(g):
    lf = g - OFF_F["op"]
    img = Image.new("RGB", (DW, DH), INK)
    d = ImageDraw.Draw(img)
    if lf < 40:  # logo slam
        d.rectangle([0, 0, DW, DH], fill=CREAM)
        speedlines(d, lf, blend(CREAM, INK, 0.15), 0.3)
        kk = 0.7 + 0.3 * pop(min(1, lf / 9))
        txt(d, (960, 470), "魔王、\n家賃を払え！", F(150 * kk, True, True), ACCENT,
            anchor="mm", stroke=7, sfill=INK)
        txt(d, (960, 700), "EPISODE 1", F(52), INK, anchor="mm")
    elif lf < 120:
        card_bg(d, lf, XCAPE, XCAPE_L, "魔王")
        sc = lerp(1.5, 1.35, prog(lf, 40, 52))
        xargoth2(d, lf, 960, 640, sc, emotion="menace", pose="idle")
        menace(d, lf, 1330, 220, ["ド", "ヤ", "ァ"], CREAM, XCAPE)
        name_tag(d, lf, 52, "魔王ザルゴス", "XARGOTH THE UNENDING",
                 "RENT: “FIAT CURRENCY IS BENEATH ME”", XCAPE)
    elif lf < 200:
        card_bg(d, lf, KHOOD, (94, 156, 212), "利用者")
        sc = lerp(1.5, 1.35, prog(lf, 120, 132))
        kenji2(d, lf, 960, 640, sc, panic=True, prop="env")
        menace(d, lf, 1290, 240, ["ア", "ワ", "ワ"], CREAM, KHOOD)
        name_tag(d, lf, 132, "田中ケンジ", "KENJI TANAKA, 26",
                 "RENT: PAYING FOR TWO", KHOOD, right=True)
    elif lf < 280:
        card_bg(d, lf, SKYB, SKYB2, "勇者")
        sc = lerp(1.7, 1.5, prog(lf, 200, 212))
        cat2(d, lf, 960, 620, sc, pose="loaf", sparkle=True)
        menace(d, lf, 1300, 240, ["キ", "ラ", "☆"], WHITE, SKYB)
        name_tag(d, lf, 212, "シニア", "“SENIOR” (THE CAT)",
                 "Definitely not the hero of legend.", (176, 138, 16))
    elif lf < 400:  # group shot
        d.rectangle([0, 0, DW, DH], fill=WALL)
        d.rectangle([0, 700, DW, DH], fill=FLOOR)
        d.ellipse([260, 750, 1660, 1010], fill=blend(FLOOR, LAMP, 0.25))
        d.polygon([(620, 620), (1300, 620), (1260, 700), (660, 700)], fill=blend(REDC, INK, 0.15))
        d.rounded_rectangle([660, 620, 1260, 730], 14, fill=TABLE, outline=INK, width=6)
        d.rectangle([700, 730, 736, 860], fill=TABLE2, outline=INK)
        d.rectangle([1184, 730, 1220, 860], fill=TABLE2, outline=INK)
        env_y = 560 + math.sin(lf / 9) * 10
        d.ellipse([830, env_y + 80, 1090, env_y + 124], fill=blend(WALL, INK, 0.3))
        d.rounded_rectangle([870, env_y - 58, 1050, env_y + 58], 10, fill=PAPER,
                            outline=INK, width=7)
        d.line([870, env_y - 58, 960, env_y + 16], fill=INK, width=6)
        d.line([1050, env_y - 58, 960, env_y + 16], fill=INK, width=6)
        txt(d, (960, env_y - 14), "家賃", F(44, True, True), ACCENT, anchor="mm")
        xargoth2(d, lf, 330, 600, 1.05, emotion="smug", pose="idle")
        kenji2(d, lf, 1600, 650, 1.05, panic=True, prop="none")
        cat2(d, lf, 700, 575, 0.95, pose="loaf")
        for i in range(18):
            seed = i * 173
            tt = ((lf * (1.4 + (i % 5) * 0.22) + seed) % 1300) / 1300
            x = (i * 337 + seed) % DW; y = -60 + tt * 1240
            if i % 3 == 0:
                d.ellipse([x - 16, y - 20, x + 16, y + 20], fill=CROWN, outline=INK, width=4)
                txt(d, (x, y - 10), "¥", F(18), INK, anchor="mm")
            else:
                d.polygon([(x, y - 14), (x + 10, y - 6), (x + 10, y + 6), (x, y + 14),
                           (x - 10, y + 6), (x - 10, y - 6)], fill=(255, 183, 197),
                          outline=INK)
        txt(d, (960, 90), "三ヶ月滞納中 — THREE MONTHS BEHIND", F(64, True, True),
            CREAM, anchor="mm", stroke=3, sfill=INK)
    else:  # finale
        d.rectangle([0, 0, DW, DH], fill=CREAM)
        speedlines(d, lf, blend(CREAM, INK, 0.12), 0.25)
        kk = 0.8 + 0.2 * pop(min(1, (lf - 404) / 9))
        txt(d, (960, 420), "魔王、家賃を払え！", F(140 * kk, True, True), ACCENT,
            anchor="mm", stroke=7, sfill=INK)
        txt(d, (960, 610), "DEMON LORD, PAY RENT!", F(52), INK, anchor="mm")
        for i, cr in enumerate(["SCREENPLAY — THE CAT", "MUSIC — CONVENIENCE STORE SPEAKERS",
                                "CATERING — 100 YEN SHOP"]):
            txt(d, (960 + (i - 1) * 560, 1000), cr, F(24, False), blend(CREAM, INK, 0.8),
                anchor="mm")
    frame = cam_apply(img, 0, 0, 1)
    dd = ImageDraw.Draw(frame)
    for t0 in (40, 120, 200, 280, 404):
        don(dd, g, OFF_F["op"] + t0, 960, 520, K)
    sub_frame(g, dd, ["n03"])
    return frame


# ============================ A-PART ============================
def seg_apart(g):
    lf = g - OFF_F["apart"]
    img = Image.new("RGB", (DW, DH), WALL)
    d = ImageDraw.Draw(img)

    if lf < 525:  # ---- A1 aftermath + shadow ----
        sh = prog(lf, 18, 99)
        apartment2(d, g, base=img, shadow=sh)
        # under-door keyring silhouette
        if 70 <= lf < 200:
            d.rectangle([1750, 700, 1890, 760], fill=blend(CREAM, LAMP, 0.5))
            d.rectangle([1770, 690, 1870, 712], fill=INK)
            for i in range(4):
                d.rectangle([1782 + i * 24, 708, 1790 + i * 24, 742], fill=INK)
        kenji2(d, g, 1330, 620, 1.05, panic=True, talking=talking("k", g),
               prop="bag")
        if lf < 360:
            xargoth2(d, g, 450, 470, 1.05, emotion="smug", talking=talking("x", g),
                     pose="idle")
        else:  # hides behind the cat
            xargoth2(d, g, 1680, 530, 0.92, emotion="panic", pose="hide")
        cat2(d, g, 1545, 575, 1.05, pose="loaf", sparkle=lf >= 440)
        if 99 <= lf < 145:
            txt(d, (1770, 240), "カチャ…カチャ…", F(40, True, True), CREAM,
                anchor="mm", stroke=4, sfill=INK)
        if 236 <= lf < 258:
            speedlines(d, lf, blend(WALL, WHITE, 0.3), 0.4, cx=1520, cy=520)
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        laugh(dd, g, 500, K, 24)
    elif lf < 1220:  # ---- A2 currency ----
        l2 = lf - 525
        apartment2(d, g, base=img)
        # chest slides in and slams
        chx = lerp(-300, 900, ease_out(prog(l2, 5, 35)))
        slammed = l2 >= 35
        if slammed:
            chx = 900
            chest(d, l2, chx, 700, 1.0,
                  open_deg=(60 * prog(l2, 90, 105) if l2 < 1116 - 525 else 0.0),
                  glow=(90 <= l2 < 275))
            if 35 <= l2 < 55:
                dust(d, l2, 35, chx, 780)
        else:
            chest(d, l2, chx, 700, 1.0)
        # points fountain
        if 90 <= l2 < 280:
            t2 = (l2 - 90) / 190
            for i in range(8):
                a = math.radians(i * 45 + 10)
                r = ease_out(t2) * (200 + (i % 3) * 60)
                fall = max(0, t2 - 0.45) * 900
                points_card(d, chx + math.cos(a) * r, 600 + math.sin(a) * r * 0.6 + fall,
                            rot=i * 33 + l2 * 2, sc=1.0)
        # characters
        xpose = "present" if 90 <= l2 < 300 else ("idle" if l2 < 560 else "hide")
        xargoth2(d, g, 620, 520, 1.05,
                 emotion=("smug" if l2 < 380 else "panic"),
                 talking=talking("x", g), pose=xpose)
        kx = 1500 + (60 if l2 > 615 else 0)
        kenji2(d, g, kx, 610, 1.05, panic=(l2 < 500), talking=talking("k", g),
               prop=("point" if 264 <= l2 < 393 else "none"))
        # word stamps for k04
        if 495 <= l2 < 580:
            words = ["POINTS.", "AT.", "TASTY.", "MART."]
            shown = [(w, 495 + i * 16) for i, w in enumerate(words) if l2 >= 495 + i * 16]
            for i, (wd, t0) in enumerate(shown):
                sc = 0.8 + 0.2 * pop(min(1, (l2 - t0) / 6))
                txt(d, (420 + i * 300, 300), wd, F(70 * sc), ACCENT,
                    anchor="mm", stroke=6, sfill=INK)
        if slammed and 591 <= l2 < 620:  # chest shut dust
            dust(d, l2, 591, chx, 700)
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        laugh(dd, g, OFF_F["apart"] + 525 + 417, K, 26)
    elif lf < 1970:  # ---- A3 diplomacy ----
        l3 = lf - 1220
        apartment2(d, g, base=img)
        # flag rises
        if l3 >= 110:
            fy = lerp(900, 660, ease_out(prog(l3, 110, 190)))
            tilt = -8 * prog(l3, 295, 330)
            import math as _m
            save = d
            flag_x(d, g, 1080, fy, 1.0)
        # cat corner "signature"
        if 295 <= l3 < 386:
            for i in range(3):
                t3 = ((l3 - 295) / 12 + i * 0.3) % 1
                dy = t3 * 60
                d.polygon([(1600 + i * 26, 780 + dy), (1610 + i * 26, 780 + dy),
                           (1605 + i * 26, 796 + dy)], fill=(140, 190, 230))
        # map unrolls, cat claims it
        if l3 >= 535:
            ms = 0.4 + 0.6 * ease_out(prog(l3, 535, 570))
            map_x(d, 960, 850, ms)
            cat2(d, g, 940, 760, 0.85 * ms, pose="loaf", sparkle=l3 >= 613)
        else:
            cat2(d, g, 1480, 580, 1.05, pose="loaf")
        xpose = "present" if 100 <= l3 < 224 else ("point" if 295 <= l3 < 430 else "idle")
        xargoth2(d, g, 620, 500, 1.05, emotion=("menace" if l3 < 224 else "smug"),
                 talking=talking("x", g), pose=xpose)
        kenji2(d, g, 1660, 645, 1.05, panic=True, talking=talking("k", g),
               prop="none")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        laugh(dd, g, OFF_F["apart"] + 1220 + 613, K, 26)
    else:  # ---- A4 employment (TASTY MART interview) ----
        l4 = lf - 1970
        tastymart2(d, g, interview=True)
        cap_on = l4 >= 612
        # resume card
        if 233 <= l4 < 390:
            t4 = l4 - 233
            s4 = 0.8 + 0.2 * pop(min(1, t4 / 8))
            d.rounded_rectangle([960 - 270 * s4, 300, 960 + 270 * s4, 560], 12,
                                fill=CREAM, outline=INK, width=7)
            txt(d, (960, 340), "RESUME", F(44 * s4), INK, anchor="mm")
            txt(d, (960, 410), "EXPERIENCE:", F(30 * s4), INK, anchor="mm")
            txt(d, (960, 452), "108 WORLDS", F(40 * s4), ACCENT, anchor="mm")
        kenji2(d, g, 700, 590, 1.0, panic=True, talking=talking("k", g), prop="none")
        xargoth2(d, g, 980, 560, 1.02,
                 emotion=("awe" if 448 <= l4 < 646 else "smug"),
                 talking=talking("x", g), pose=("idle" if l4 < 448 else "fist"),
                 cap=cap_on, apron=cap_on)
        minor_person(d, g, 1420, 560, 1.02, shirt=TM_GREEN,
                     talking=talking("m", g), flip=True, cap_color=TM_RED)
        if 590 <= l4 < 612:  # cap falls onto Xargoth
            capy = lerp(120, -88, ease_io(prog(l4, 590, 612)))
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        laugh(dd, g, OFF_F["apart"] + 1970 + 655, K, 26)
    # banners + dons + subtitles + wipes
    dd = ImageDraw.Draw(frame)
    if lf < 525:
        pass
    elif lf < 1220:
        banner(dd, g, OFF_F["apart"] + 525 + 12, "EXCUSE #1", "CURRENCY")
    elif lf < 1970:
        banner(dd, g, OFF_F["apart"] + 1220 + 19, "EXCUSE #2", "DIPLOMACY")
    else:
        banner(dd, g, OFF_F["apart"] + 1970 + 19, "EXCUSE #3", "EMPLOYMENT")
    for w0 in (520, 1214, 1964, 2692):
        draw_wipe(dd, g, OFF_F["apart"] + w0)
    don(dd, g, OFF_F["apart"] + 560, 900, 640, K)
    don(dd, g, OFF_F["apart"] + 900, 620, 400, K)
    don(dd, g, OFF_F["apart"] + 2740, 960, 400, K)
    sub_frame(g, dd, ["n04", "n05", "k02", "x03", "x04", "n06",
                      "n07", "x05", "k03", "x06", "k04", "n08",
                      "n09", "x07", "n10", "k05", "n11",
                      "n12", "k06", "x08", "m01", "x09", "n13"])
    return frame


# ============================ EYECATCH ============================
def seg_eye(g):
    lf = g - OFF_F["eye"]
    img = Image.new("RGB", (DW, DH), CREAM)
    d = ImageDraw.Draw(img)
    speedlines(d, lf, blend(CREAM, INK, 0.10), 0.18)
    bA = abs(math.sin(lf / 7)) * 26
    bB = abs(math.sin(lf / 7 + math.pi / 2)) * 26
    d.ellipse([430, 854, 810, 906], fill=blend(CREAM, INK, 0.18))
    d.ellipse([1150, 854, 1450, 902], fill=blend(CREAM, INK, 0.18))
    xargoth2(d, lf, 620, 700 - bA, 0.85, emotion="smug", pose="idle")
    cat2(d, lf, 1300, 760 - bB, 0.8, pose="loaf", sparkle=True)
    for i in range(3):
        on = math.sin(lf / 6 - i * 1.2) > 0
        d.ellipse([890 + (i - 1) * 70 - 16, 178, 890 + (i - 1) * 70 + 16, 210],
                  fill=ACCENT if on else blend(CREAM, ACCENT, 0.25), outline=INK, width=5)
    txt(d, (960, 96), "Ａパート終了", F(72, True, True), INK, anchor="mm")
    txt(d, (960, 930), "SEE YOU AFTER THE BREAK!", F(54), ACCENT, anchor="mm",
        stroke=2, sfill=INK)
    return cam_apply(img, 0, 0, 1)


# ============================ B-PART ============================
def seg_bpart(g):
    lf = g - OFF_F["bpart"]
    img = Image.new("RGB", (DW, DH), TM_WALL)
    d = ImageDraw.Draw(img)

    if lf < 750:  # ---- B1 montage ----
        tastymart2(d, g)
        xargoth2(d, g, 1550, 470, 1.05, emotion="menace",
                 talking=talking("x", g),
                 pose=("point" if 156 <= lf < 273 else "idle"), cap=True, apron=True)
        # onigiri army ranks
        for r in range(2):
            for i in range(7):
                wob = 3 * math.sin(g / 9 + i) if lf >= 156 else 0
                onigiri(d, 300 + i * 84, 470 + r * 70 + wob, 1.0)
        if 156 <= lf < 273:
            speedlines(d, lf, blend(TM_WALL, WHITE, 0.4), 0.35, cx=640, cy=440)
            d.line([1350, 380, 900, 430], fill=INK, width=8)
            d.ellipse([880, 414, 910, 444], fill=ACCENT, outline=INK, width=4)
        cut = (lf - 273) // 66 if lf >= 273 else -1
        if cut == 0:  # shelf zoom sparkle
            d.rectangle([180, 330, 640, 560], outline=CROWN, width=8)
            txt(d, (410, 310), "PERFECT", F(44), CROWN, anchor="mm", stroke=4, sfill=INK)
        elif cut == 1:  # register + coins
            for i in range(6):
                t1 = ((lf * 3 + i * 40) % 120) / 120
                d.ellipse([1240 + i * 24, 520 - t1 * 260 - 14, 1268 + i * 24, 520 - t1 * 260 + 14],
                          fill=CROWN, outline=INK, width=3)
        elif cut == 2:  # happy customer silhouette
            minor_person(d, lf, 700, 560, 1.0, shirt=(200, 130, 70))
            txt(d, (700, 380), "☆☆☆☆☆", F(44), CROWN, anchor="mm", stroke=3, sfill=INK)
        elif cut == 3:  # floor sparkle
            for i in range(10):
                a = math.radians(i * 36 + lf)
                r = 60 + 30 * math.sin(lf / 5 + i)
                x0, y0 = 700 + math.cos(a) * r * 2.4, 760 + math.sin(a) * r * 0.5
                d.polygon([(x0, y0 - 14), (x0 + 5, y0), (x0, y0 + 14), (x0 - 5, y0)],
                          fill=WHITE)
        # sales up / morale down chart
        if 540 <= lf < 640:
            d.rounded_rectangle([900, 200, 1500, 430], 10, fill=CREAM, outline=INK, width=6)
            txt(d, (1200, 232), "NIGHT ONE", F(34), INK, anchor="mm")
            d.line([950, 380, 1180, 250], fill=TM_GREEN, width=10)
            d.polygon([(1180, 250), (1150, 262), (1168, 278)], fill=TM_GREEN)
            txt(d, (1060, 300), "SALES", F(24), TM_GREEN, anchor="mm")
            d.line([1230, 250, 1460, 380], fill=TM_RED, width=10)
            d.polygon([(1460, 380), (1430, 368), (1448, 352)], fill=TM_RED)
            txt(d, (1340, 330), "MORALE", F(24), TM_RED, anchor="mm")
        if lf >= 460:
            kenji2(d, g, 380, 690, 1.02, panic=False, prop="mop")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
    elif lf < 1410:  # ---- B2 complaint / war ----
        l2 = lf - 750
        tastymart2(d, g)
        # SOLD OUT tag on pudding slot
        if 18 <= l2 < 300:
            d.rounded_rectangle([420, 420, 560, 470], 6, fill=CREAM, outline=INK, width=4)
            txt(d, (490, 445), "SOLD OUT", F(24), TM_RED, anchor="mm")
        customer_here = l2 < 150
        if customer_here:
            minor_person(d, g, 700, 560, 1.02, shirt=(200, 130, 70),
                         talking=talking("c", g), flip=True)
        # xargoth rises at don
        rise = ease_out(prog(l2, 150, 165))
        xargoth2(d, g, 1550, 470 - 0, 1.05 + 0.0,
                 emotion=("menace" if 150 <= l2 < 462 else "smug"),
                 talking=talking("x", g),
                 pose=("fist" if 358 <= l2 < 462 else "idle"), cap=True, apron=True)
        if 150 <= l2 < 200:
            speedlines(d, lf, blend(TM_WALL, REDC, 0.4), 0.4, cx=1550, cy=380)
        if 300 <= l2 < 354:
            kenji2(d, g, 300, 600, 1.05, panic=True, talking=talking("k", g),
                   prop="none")
            d.polygon([(340, 520), (352, 498), (326, 500)], fill=ACCENT)
        if 358 <= l2 < 462:  # war declaration
            pulse = 0.5 + 0.3 * math.sin(lf / 3)
            d.rectangle([0, 0, DW, DH], fill=blend(REDC, (0, 0, 0), 0.55 - 0.2 * pulse))
            tastymart2(d, g) if False else None
            sc = 0.7 + 0.3 * pop(min(1, (l2 - 390) / 8))
            d.rounded_rectangle([960 - 280 * sc, 260 - 90 * sc, 960 + 280 * sc, 260 + 90 * sc],
                                14, fill=TM_RED, outline=CREAM, width=8)
            txt(d, (960, 260), "宣戦布告", F(90 * sc, True, True), CREAM, anchor="mm")
            txt(d, (960, 380), "WAR DECLARATION", F(36 * sc), CREAM, anchor="mm")
        if 480 <= l2 < 575:  # one-star review
            review_card(d, 960, 420, 1.0, stars_filled=1, t=(l2 - 480) / 8)
            xargoth2(d, g, 1550, 500, 1.0, emotion="panic", pose="hide",
                     cap=True, apron=True)
        if customer_here and 30 <= l2 < 91:
            d.ellipse([640, 300, 680, 340], outline=(220, 130, 60), width=5)
            txt(d, (760, 320), "?", F(60), (220, 130, 60), anchor="mm")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
    elif lf < 2100:  # ---- B3 payday ----
        l3 = lf - 1410
        tastymart2(d, g)
        sil0 = (E["payday_silence"][0] - OFF_F["bpart"]) * 1.0
        # envelope rises from register with glow (payday)
        env_y = lerp(700, 480, ease_out(prog(l3, 30, 120)))
        envelope_glow(d, g, 1330, env_y)
        d.rounded_rectangle([1330 - 70, env_y - 46, 1330 + 70, env_y + 46], 8,
                            fill=PAPER, outline=INK, width=7)
        d.line([1330 - 70, env_y - 46, 1330, env_y + 12], fill=INK, width=5)
        d.line([1330 + 70, env_y - 46, 1330, env_y + 12], fill=INK, width=5)
        txt(d, (1330, env_y + 22), "¥46,000", F(26), ACCENT, anchor="mm")
        if l3 < 164:  # kenji in bg during payday narration
            kenji2(d, g, 430, 680, 1.0, panic=False, prop="none")
        if 164 <= l3 < 233:  # hold (silence)
            pass
        if l3 >= 164:
            xpose = "formal" if l3 < 308 else "idle"
            xemo = "awe" if 164 <= l3 < 308 else "smug"
            xargoth2(d, g, 1050, 500, 1.06, emotion=xemo,
                     talking=talking("x", g) and 164 <= l3 < 400, pose=xpose)
        # cat deadpan closeup
        if 308 <= l3 < 360:
            cat2(d, g, 1500, 260, 1.5, pose="loaf")
        if l3 >= 420:
            kenji2(d, g, 430, 680, 1.02, panic=False, talking=talking("k", g),
                   prop=("smile" if l3 < 554 else "none"))
        if l3 >= 554:  # second shift determination
            xargoth2(d, g, 1050, 470, 1.08, emotion="menace",
                     talking=talking("x", g), pose="fist")
            speedlines(d, lf, blend(TM_WALL, CROWN, 0.25), 0.3, cx=1050, cy=380)
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        laugh(dd, g, OFF_F["bpart"] + 1410 + 379, K, 26)
    else:  # ---- B4 tag: Obaa-san ----
        l4 = lf - 2100
        apartment2(d, g, base=img)
        obx = lerp(2050, 1720, ease_out(prog(l4, 0, 40)))
        doom = l4 >= 222
        obaa2(d, g, obx, 620, 0.98, doom=doom, talking=talking("o", g))
        if l4 >= 222:
            menace(d, g, 1500, 240, ["ゴ", "ゴ", "ゴ"], CROWN, WALL, size=58)
        xpose = "formal" if 111 <= l4 < 323 else ("kneel" if l4 >= 323 else "idle")
        xemo = "panic" if l4 >= 222 else "smug"
        xargoth2(d, g, 1150, 540, 1.05, emotion=xemo,
                 talking=talking("x", g), pose=xpose)
        kenji2(d, g, 560, 620, 1.0, panic=(l4 >= 222), prop="bag")
        if l4 >= 323:  # collapse ring
            t4 = l4 - 323
            rr = min(1, t4 / 14)
            d.ellipse([1150 - 400 * rr, 500 - 300 * rr, 1150 + 400 * rr, 500 + 300 * rr],
                      outline=blend(CROWN, WALL, rr), width=max(2, int(14 * (1 - rr))))
        if l4 >= 540:
            txt(d, (960, 830), "つづく", F(72, True, True), CREAM, anchor="mm",
                stroke=4, sfill=INK)
        if l4 >= 570:
            txt(d, (960, 930), "meow.", F(40, False), HALO, anchor="mm")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        frame = vignette(frame, 0.3) if l4 >= 323 else frame
        dd = ImageDraw.Draw(frame)
    # subtitles + dons + wipes
    dd = ImageDraw.Draw(frame)
    for w0 in (742, 1402, 2092):
        draw_wipe(dd, g, OFF_F["bpart"] + w0)
    don(dd, g, OFF_F["bpart"] + 900, 1550, 300, K)
    don(dd, g, OFF_F["bpart"] + 1140, 960, 260, K)
    sub_frame(g, dd, ["n14", "x10", "n15", "c01", "x11", "k07", "x12", "n16",
                      "n17", "x13", "n18", "k08", "x14",
                      "n19", "x15", "o01", "x16"])
    return frame


# ============================ END CARD ============================
def seg_end(g):
    lf = g - OFF_F["end"]
    img = Image.new("RGB", (DW, DH), INK)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 90, 1830, 990], 20, outline=blend(INK, CREAM, 0.4), width=6)
    if lf > 8:
        txt(d, (960, 170), "NEXT EPISODE", F(56), HALO, anchor="mm")
    txt(d, (960, 280), "第二話「深淵のWi-Fiパスワード」", F(78, True, True), CREAM, anchor="mm")
    txt(d, (960, 370), "Ep. 2 — “The WiFi Password of the Abyss”", F(38, False),
        (184, 169, 208), anchor="mm")
    # router tease on kotatsu silhouette
    d.rounded_rectangle([880, 560, 1040, 620], 10, fill=(58, 58, 74), outline=CREAM, width=4)
    d.line([900, 560, 880, 500], fill=CREAM, width=5)
    d.line([1020, 560, 1040, 500], fill=CREAM, width=5)
    led = LED_G if (lf % 40) < 24 else LED_R
    d.ellipse([1010, 586, 1028, 604], fill=led)
    # cat walks off carrying the router
    catX = lerp(-260, 2150, ease_io(min(1, max(0, (lf - 240) / 110))))
    cat2(d, g, catX, 940, 0.7, pose="loaf")
    if lf > 150:
        txt(d, (960, 700), "DEMON LORD, PAY RENT! — Episode 1", F(36, False),
            blend(INK, CREAM, 0.9), anchor="mm")
    frame = cam_apply(img, 0, 0, 1)
    dd = ImageDraw.Draw(frame)
    sub_frame(g, dd, ["x16", "n19", "x17", "k09"])
    return frame


SEGS_FN = [
    (S["cold"]["start"] * FPS, S["cold"]["end"] * FPS, seg_cold),
    (S["op"]["start"] * FPS, S["op"]["end"] * FPS, seg_op),
    (S["apart"]["start"] * FPS, S["apart"]["end"] * FPS, seg_apart),
    (S["eye"]["start"] * FPS, S["eye"]["end"] * FPS, seg_eye),
    (S["bpart"]["start"] * FPS, S["bpart"]["end"] * FPS, seg_bpart),
    (S["end"]["start"] * FPS, S["end"]["end"] * FPS, seg_end),
]


def render_frame(g):
    for a, b, fn in SEGS_FN:
        if a <= g < b:
            return fn(g)
    return seg_end(min(g, TOTAL_F_END - 1))


TOTAL_F_END = TL["total_frames"]
