#!/usr/bin/env python3
"""DLPR Ep2 FULL — segment renderers (cold / op / apart / eye / bpart / end).

「深淵のWi-Fiパスワード」Each seg_*(g) takes the ABSOLUTE frame index and
returns a 1280x720 RGB frame. Dialogue windows come from timeline.json.
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
    apartment2, tastymart2, points_card, onigiri, envelope_glow, vignette,
    draw_wipe,
)
from dlpr_props2 import (
    router2, crown2, receipt2, note2, bid_board, microwave2, wifi_sign,
    lease_folder, zap, static_fx, stamp,
)

E = EVENTS
S = {s["name"]: s for s in TL["segs"]}
OFF = {k2: S[k2]["start"] for k2 in S}
OFF_F = {k2: S[k2]["start"] * FPS for k2 in S}

SPK = {"x": (XCAPE, "XARGOTH"), "k": (KHOOD, "KENJI"),
       "n": ((212,180,40), "SENIOR (THE CAT)"), "m": ((60,160,90), "MANAGER"),
       "c": ((220,130,60), "CUSTOMER"), "o": ((190,80,110), "OBAA-SAN")}

TXT = {L["id"]: L["text"] for L in TL["lines"]}

JP = {
 "n01": "アパート302号室、土曜朝6時。魔王は最も聖なる儀式のために起きた。それは…ルーター",
 "x01": "跪け、星の小箱よ。深淵を我が電話に注げ",
 "k01": "火曜から赤だ。あれは家賃ライトだ",
 "x02": "家賃用の…ライトなのか？",
 "n02": "ライトは何にでもある。選択肢以外は",
 "n03": "王冠一つ、借金一つ、電波ゼロ",
 "n04": "計画は簡単だった。王冠をネットに売る",
 "n05": "その計画には…ネットが必要だった",
 "k02": "ネットは停止中。理由は家賃。家賃はお前だ",
 "x03": "ならば王冠を競売に。底価23万8千円",
 "n06": "不足額ぴったりの値段。心が痛む",
 "n07": "作戦一：武力行使",
 "x04": "起きろ機械よ。我は無限の魔王ザルゴス。保証書のことも思い出せ",
 "k03": "つまりコンセントを抜いて差し直せという意味だ",
 "n08": "古の儀式は執り行われた",
 "x05": "生き返った—",
 "n09": "4秒生きた。そして家賃を思い出した",
 "n10": "作戦二：総当たりの深淵",
 "x06": "深淵には名前がある。「ザルゴス」「ザルゴス」「zalgo666」",
 "k04": "あのrouterは大家のだ。「obaa」＋数字だ",
 "x07": "ならば深淵に示そう：obaa1、obaa12、obaa123",
 "n11": "41回目。丁寧に拒否された",
 "k05": "ロックアウト30分。レイドボスかよ",
 "n12": "作戦三：外交",
 "x08": "対等に語らおう。我と、この建物の所有者と",
 "k06": "それ、三月と同じIOUだろ",
 "n13": "扉は4センチ開いた。一枚の紙切れが現れた",
 "x09": "「家賃再開の時、Wi-Fi復活」。韻を踏んだ！準備していたんだ！",
 "n14": "戦争会議は11秒で終わった",
 "n15": "夜勤。この界隈最後の無料Wi-Fi",
 "m01": "パスワードはレシートに。レシートは購入者に",
 "x10": "値を付けろ門番よ。無限の王冠、最高額入札者を待つ。我が求めるは…プリン一つ",
 "k08": "最後のプリン。小銭で払った",
 "n16": "レシートにはこうあった：「obaa0302」",
 "x11": "深淵とは…プリンだったのか",
 "n17": "出品開始。「呪われし王冠・少し泣く」",
 "c01": "「泣く」のは…仕様ですか？",
 "x12": "王冠は不適合者のためにだけ泣く。汝は通れ",
 "k09": "マイロード、品出しを。おにぎりが労組を結成した",
 "n18": "9時40分、入札は15万円に",
 "x13": "誰だ、勝手に温めたのは",
 "m02": "電子レンジは必須設備だ。レンジへの宣戦は許さない",
 "x14": "ならば待つ。潮のように。ダンジョンのように",
 "n19": "9時58分、入札は23万8千円ちょうど",
 "k10": "残り60秒。息をするな。何も温めるな",
 "n20": "出品は圏外のまま終了。落札者…「obaa_god_777」",
 "x15": "…王冠は金のためではなかった",
 "k11": "全部金のためだった",
 "n21": "閉店時、最後の客が来た。もう買った後だった",
 "o01": "23万8千円。受け取りは私。王冠は被ったままでいい",
 "o02": "利息は免除。今回だけだよ",
 "x16": "家賃：完済。尊厳：保留",
 "k12": "パスワードが…賃貸契約書にあった！9ページ、設備欄に！",
 "x17": "知っている。俺が署名した",
 "n22": "封されていたのは彼ではない。猫だ",
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


def pw_card(d, x, y, word, t, dead=False):
    """Floating wrong-password card."""
    s = 0.7 + 0.3 * pop(min(1, max(0, t)))
    w2, h2 = (30 + 11 * len(word)) * s, 44 * s
    d.rounded_rectangle([x - w2, y - h2, x + w2, y + h2], 8 * s,
                        fill=blend(CREAM, INK, 0.06), outline=INK, width=max(2, int(4 * s)))
    txt(d, (x, y), word, F(26 * s, True, False), INK, anchor="mm")
    if dead:
        c = 34 * s
        d.line([x - c, y - c, x + c, y + c], fill=REDC, width=max(3, int(8 * s)))
        d.line([x - c, y + c, x + c, y - c], fill=REDC, width=max(3, int(8 * s)))


def sub_frame(g, dd, lids):
    for lid in lids:
        color, name = SPK[lid[:1]]
        subtitle(dd, g, lid, name, color, TXT[lid], jp=JP.get(lid), cat=(lid[:1] == "n"))


# ============================ COLD OPEN ============================
def seg_cold(g):
    lf = g - OFF_F["cold"]
    img = Image.new("RGB", (DW, DH), WALL)
    d = ImageDraw.Draw(img)
    frozen = g >= E["freeze_f"]
    fz = E["freeze_f"] if frozen else g
    drift = lerp(120, 0, prog(lf, 0, 60))

    apartment2(d, g, base=img)

    # router on the kotatsu — the fallen god
    router2(d, fz, 1560, 585, 1.05, led="red")
    if 330 <= lf < 470:  # horror aura at the reveal
        menace(d, fz, 1440, 300, ["ピ", "ッ"], CREAM, WALL, size=58)
        if 350 <= lf < 420:
            speedlines(d, fz, blend(WALL, REDC, 0.35), 0.35, cx=1560, cy=560)
    # Xargoth: enters, reveres, realises
    xarX = lerp(260, 640, ease_out(prog(lf, 0, 70)))
    pose = "present" if lf < 258 else ("formal" if lf < 460 else "hide")
    emo = "smug" if lf < 258 else ("awe" if lf < 460 else "panic")
    xargoth2(d, fz, xarX + drift, 480, 1.05, emotion=emo,
             talking=talking("x", g), pose=pose)
    if 60 <= lf < 250:
        menace(d, fz, 780 + drift, 300, ["儀", "式"], CREAM, WALL, size=52)
    # Kenji enters with the truth
    kenX = lerp(2100, 1450, ease_out(prog(lf, 413, 435)))
    kenji2(d, fz, kenX + drift, 620, 1.05, panic=True,
           talking=talking("k", g), prop="point")
    if 415 <= lf < 445:
        speedlines(d, fz, blend(WALL, WHITE, 0.35), 0.5, cx=1500, cy=500)
    # snap → LED white flash
    snap_f = int(E["snap_t"] * FPS)
    if snap_f <= g < snap_f + 8:
        d.ellipse([1440, 500, 1700, 680], outline=WHITE, width=10)
        txt(d, (1560, 470), "ピンッ", F(70, True, True), WHITE,
            anchor="mm", stroke=6, sfill=INK)
    # THE CAT, unbothered, on the sofa
    cat2(d, fz, 300 + drift, 545, 1.05, pose=("sit" if frozen else "loaf"),
         sparkle=frozen)

    # camera: drift → push → freeze zoom to Xargoth's face
    sx, sy = (shake(lf, 5) if 420 <= lf < 436 else (0, 0))
    push = prog(lf, 279, 413)
    cam_x = lerp(0, -60, ease_out(push)) + sx
    cam_s = lerp(1.0, 1.06, ease_out(push))
    zt = prog(g, E["freeze_f"] - 20, E["freeze_f"])
    ze = ease_out(zt)
    cam_x = lerp(cam_x, -420, ze); cam_y = lerp(0, 60, ze); cam_s = lerp(cam_s, 1.9, ze)
    frame = cam_apply(img, cam_x, cam_y, cam_s)

    dd = ImageDraw.Draw(frame)
    if lf < 60:
        dd.rounded_rectangle([32 * K, 32 * K, 330 * K, 86 * K], 10 * K, fill=INK)
        txt(dd, (50 * K, 42 * K), "COLD OPEN", F(34 * K), CREAM)
    if frozen:
        txt(dd, (940 * K, 330 * K), "RECORD SCRATCH ♪", F(40), CREAM,
            anchor="mm", stroke=5, sfill=INK)
        menace(dd, fz, 1250, 430, ["ピ", "ク"], CREAM, WALL, size=56)
        frame = vignette(frame, 0.45)
        dd = ImageDraw.Draw(frame)
    laugh(dd, g, 470, K, 24)
    don(dd, g, 426, 1460, 330, K)
    sub_frame(g, dd, ["n01", "x01", "k01", "x02", "n02"])
    dd2 = frame
    if g >= E["freeze_f"] + 74:
        dd2 = flash(frame, g, E["freeze_f"] + 74, 6)
        dd = ImageDraw.Draw(dd2)
        dd.rectangle([0, 0, W, H], fill=CREAM)
        speedlines(dd, g, blend(CREAM, INK, 0.15), 0.3, cx=W / 2, cy=H / 2, k=K)
        sc = 0.7 + 0.3 * pop(min(1, (g - E["freeze_f"] - 78) / 9))
        txt(dd, (W / 2, H / 2 - 10), "魔王、家賃を払え！", F(84 * sc, True, True),
            ACCENT, anchor="mm", stroke=7, sfill=INK)
        txt(dd, (W / 2, H / 2 + 90), "EPISODE 2 — THE WIFI PASSWORD OF THE ABYSS",
            F(30 * sc), INK, anchor="mm")
        don(dd, g, E["freeze_f"] + 80, 960 * K, 540 * K, K)
    return dd2


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
        txt(d, (960, 700), "EPISODE 2", F(52), INK, anchor="mm")
    elif lf < 120:
        card_bg(d, lf, XCAPE, XCAPE_L, "魔王")
        sc = lerp(1.5, 1.35, prog(lf, 40, 52))
        xargoth2(d, lf, 960, 640, sc, emotion="menace", pose="phone")
        router2(d, lf, 1520, 700, 0.85, led="red")
        menace(d, lf, 1330, 220, ["圏", "外"], CREAM, XCAPE)
        name_tag(d, lf, 52, "魔王ザルゴス", "XARGOTH THE UNENDING",
                 "Wi-Fi: REVOKED", XCAPE)
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
        router2(d, lf, 1420, 800, 0.7, led="red")
        menace(d, lf, 1300, 240, ["キ", "ラ", "☆"], WHITE, SKYB)
        name_tag(d, lf, 212, "シニア", "“SENIOR” (THE CAT)",
                 "Definitely not the hero of legend.", (176, 138, 16))
    elif lf < 400:  # group shot — the dead router on the kotatsu
        d.rectangle([0, 0, DW, DH], fill=WALL)
        d.rectangle([0, 700, DW, DH], fill=FLOOR)
        d.ellipse([260, 750, 1660, 1010], fill=blend(FLOOR, LAMP, 0.25))
        d.polygon([(620, 620), (1300, 620), (1260, 700), (660, 700)], fill=blend(REDC, INK, 0.15))
        d.rounded_rectangle([660, 620, 1260, 730], 14, fill=TABLE, outline=INK, width=6)
        d.rectangle([700, 730, 736, 860], fill=TABLE2, outline=INK)
        d.rectangle([1184, 730, 1220, 860], fill=TABLE2, outline=INK)
        router2(d, lf, 960, 660, 0.95, led="red")
        for i in range(3):  # dying Wi-Fi arcs
            r = 40 + i * 34
            on = (lf % 36) < 12 + i * 8
            d.arc([960 - r, 480 - r, 960 + r, 480 + r], 220, 320,
                  fill=blend(WALL, REDC, 0.75) if on else blend(WALL, INK, 0.4), width=8)
        xargoth2(d, lf, 330, 600, 1.05, emotion="panic", pose="idle")
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
        txt(d, (960, 90), "圏外 — NO SIGNAL", F(64, True, True),
            CREAM, anchor="mm", stroke=3, sfill=INK)
    else:  # finale
        d.rectangle([0, 0, DW, DH], fill=CREAM)
        speedlines(d, lf, blend(CREAM, INK, 0.12), 0.25)
        kk = 0.8 + 0.2 * pop(min(1, (lf - 404) / 9))
        txt(d, (960, 420), "魔王、家賃を払え！", F(140 * kk, True, True), ACCENT,
            anchor="mm", stroke=7, sfill=INK)
        txt(d, (960, 610), "DEMON LORD, PAY RENT!", F(52), INK, anchor="mm")
        for i, cr in enumerate(["SCREENPLAY — THE CAT", "SPONSOR — THE MICROWAVE",
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
PW_WORDS = ["Xargoth", "XARGOTH", "xargoth666", "THE_UNENDING_ONE",
            "obaa1", "obaa12", "obaa123", "password123"]


def seg_apart(g):
    lf = g - OFF_F["apart"]
    img = Image.new("RGB", (DW, DH), WALL)
    d = ImageDraw.Draw(img)

    if lf < 525:  # ---- A1 morning after: the plan ----
        apartment2(d, g, base=img, day=True)
        crown2(d, 300, 262, 0.85, glow=(lf % 90 < 45), f=g)
        router2(d, g, 1560, 580, 1.0, led="red")
        pose = "present" if 60 <= lf < 350 else "idle"
        xargoth2(d, g, 620, 500, 1.05, emotion=("smug" if lf < 470 else "panic"),
                 talking=talking("x", g), pose=pose)
        kenji2(d, g, 1700, 630, 1.02, panic=True, talking=talking("k", g),
               prop=("bag" if lf < 300 else "none"))
        cat2(d, g, 1240, 560, 0.9, pose="loaf")
        if 150 <= lf < 320:  # auction plans hovering
            d.rounded_rectangle([900, 180, 1460, 300], 12, fill=CREAM, outline=INK, width=6)
            txt(d, (1180, 218), "PLAN: AUCTION", F(38, True, False), INK, anchor="mm")
            txt(d, (1180, 268), "the crown. online.", F(26, False, False),
                blend(CREAM, INK, 0.6), anchor="mm")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
    elif lf < 1220:  # ---- A2 plan one: overwhelming force ----
        l2 = lf - 525
        apartment2(d, g, base=img, day=True)
        # router on a stool, center stage
        rled = "red"
        if g >= int(E["hope_t"] * FPS) and g < int(E["die_t"] * FPS):
            rled = "green"
        elif g >= int(E["plug_t"] * FPS) and g < int(E["hope_t"] * FPS):
            rled = "off"
        router2(d, g, 960, 640, 1.15, led=rled, glow=(rled == "green"),
                cable=(g < int(E["plug_t"] * FPS)))
        d.rectangle([900, 660, 1020, 760], fill=TABLE2, outline=INK, width=5)
        # Kenji performs the rite
        kplug = g >= int(E["plug_t"] * FPS) - 8
        kenji2(d, g, 1330 if not kplug else 1240, 620, 1.02,
               panic=(l2 < 500), talking=talking("k", g),
               prop=("none" if kplug else "point"))
        zap(d, g, int(E["plug_t"] * FPS), 1000, 620)
        if int(E["plug_t"] * FPS) - 4 <= g < int(E["plug_t"] * FPS) + 18:
            dust(d, g, int(E["plug_t"] * FPS), 960, 700)
        xemo = "menace" if l2 < 420 else ("awe" if rled == "green" else "panic")
        xpose = "fist" if l2 < 420 else ("present" if rled == "green" else "hide")
        xargoth2(d, g, 560, 500, 1.05, emotion=xemo, talking=talking("x", g),
                 pose=xpose)
        if l2 < 420:
            speedlines(d, g, blend(WALL, REDC, 0.25), 0.30, cx=960, cy=560)
            menace(d, g, 700, 260, ["武", "力"], CREAM, WALL, size=58)
        if rled == "green":
            for i in range(2):
                d.arc([880 - 60 - i * 26, 560 - 60 - i * 26, 880 + 60 + i * 26,
                       560 + 60 + i * 26], -70, 70, fill=LED_G, width=8)
            txt(d, (1180, 420), "回線、復活…？", F(40, True, True), LED_G,
                anchor="mm", stroke=4, sfill=INK)
        if g >= int(E["die_t"] * FPS):
            txt(d, (960, 200), "圏外", F(64, True, True), REDC,
                anchor="mm", stroke=4, sfill=INK)
        cat2(d, g, 1650, 560, 0.9, pose="loaf")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
    elif lf < 1970:  # ---- A3 plan two: the guessing abyss ----
        l3 = lf - 1220
        apartment2(d, g, base=img, day=True)
        router2(d, g, 1520, 570, 1.1, led="red")
        # floating wrong-password cards
        t_brute = int(E["brute_t"] * FPS)
        n11_f = line_window("n11")[1]
        for i, wd in enumerate(PW_WORDS):
            t0 = t_brute + 20 + i * 34
            if t0 <= g < n11_f:
                cxx = 300 + (i % 4) * 380
                cyy = 300 + (i // 4) * 180 + (i % 3) * 40
                pw_card(d, cxx, cyy, wd, (g - t0) / 9, dead=(g >= t0 + 22))
                if t0 <= g < t0 + 3:
                    d.rectangle([0, 0, DW, DH], fill=blend(WALL, REDC, 0.18))
        # lockout panel after n11
        if g >= line_window("n11")[1]:
            d.rounded_rectangle([1180, 180, 1760, 340], 12, fill=INK, outline=REDC, width=6)
            txt(d, (1470, 228), "ACCESS LOCKED", F(34, True, False), REDC, anchor="mm")
            txt(d, (1470, 290), "COOL-DOWN: 30:00", F(28, True, False), CREAM, anchor="mm")
        xpose = "phone" if l3 < 640 else "hide"
        xargoth2(d, g, 620, 500, 1.05, emotion=("menace" if l3 < 500 else "panic"),
                 talking=talking("x", g), pose=xpose)
        kenji2(d, g, 1000, 630, 1.0, panic=False, talking=talking("k", g),
               prop="none")
        cat2(d, g, 420, 560, 0.85, pose="loaf")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
    else:  # ---- A4 plan three: diplomacy at the door ----
        l4 = lf - 1970
        sh_t = int(E["shadow_t"] * FPS)
        sh = prog(g, sh_t, sh_t + 75)
        apartment2(d, g, base=img, day=True, shadow=sh)
        # under-door keyring silhouette
        if g >= sh_t + 30 and sh > 0.2:
            d.rectangle([1750, 700, 1890, 760], fill=blend(CREAM, LAMP, 0.5))
            d.rectangle([1770, 690, 1870, 712], fill=INK)
            for i in range(4):
                d.rectangle([1782 + i * 24, 708, 1790 + i * 24, 742], fill=INK)
        # the offering tray (IOUs + one mandarin)
        x09_f = line_window("x09")[0]
        xargoth2(d, g, 1150, 520, 1.05,
                 emotion=("panic" if g >= x09_f else "smug"),
                 talking=talking("x", g),
                 pose=("fist" if g >= x09_f else "present"))
        d.ellipse([1150 - 120, 610, 1150 + 120, 658], fill=TABLE, outline=INK, width=5)
        for i in range(3):
            d.rectangle([1150 - 90 + i * 62, 586, 1150 - 50 + i * 62, 622],
                        fill=PAPER, outline=INK, width=3)
            txt(d, (1150 - 70 + i * 62, 604), "IOU", F(15, False, False), INK, anchor="mm")
        d.ellipse([1150 + 40, 578, 1150 + 92, 626], fill=(240, 140, 50), outline=INK, width=3)
        # the note slides out
        n13_f = line_window("n13")[0]
        if g >= n13_f:
            nx = lerp(1760, 1480, ease_out(prog(g, n13_f, n13_f + 40)))
            note2(d, nx, 760, 0.62, t=(g - n13_f) / 9)
        kenji2(d, g, 560, 620, 1.0, panic=True, talking=talking("k", g), prop="bag")
        cat2(d, g, 300, 560, 0.95, pose="sit")
        if x09_f - 20 <= g < x09_f + 120:
            speedlines(d, g, blend(WALL, REDC, 0.3), 0.35, cx=1150, cy=420)
        # war cabinet collapse ring
        n14_f = line_window("n14")[0]
        if g >= n14_f:
            t4 = g - n14_f
            rr = min(1, t4 / 14)
            d.ellipse([1150 - 400 * rr, 480 - 300 * rr, 1150 + 400 * rr, 480 + 300 * rr],
                      outline=blend(CROWN, WALL, rr), width=max(2, int(14 * (1 - rr))))
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        frame = vignette(frame, 0.3) if g >= n14_f else frame
        dd = ImageDraw.Draw(frame)
    # banners + dons + wipes + laughs + subtitles
    dd = ImageDraw.Draw(frame)
    if lf < 525:
        pass
    elif lf < 1220:
        banner(dd, g, OFF_F["apart"] + 525 + 12, "PLAN #1", "OVERWHELMING FORCE")
    elif lf < 1970:
        banner(dd, g, OFF_F["apart"] + 1220 + 19, "PLAN #2", "THE GUESSING ABYSS")
    else:
        banner(dd, g, OFF_F["apart"] + 1970 + 19, "PLAN #3", "DIPLOMACY")
    for w0 in (520, 1214, 1964, 2692):
        draw_wipe(dd, g, OFF_F["apart"] + w0)
    don(dd, g, OFF_F["apart"] + 560, 900, 640, K)
    don(dd, g, OFF_F["apart"] + 900, 620, 400, K)
    don(dd, g, OFF_F["apart"] + 2740, 960, 400, K)
    for lt in E["laugh_t"][:4]:
        laugh(dd, g, int(lt * FPS), K, 26)
    sub_frame(g, dd, ["n04", "n05", "k02", "x03", "n06",
                      "n07", "x04", "k03", "n08", "x05", "n09",
                      "n10", "x06", "k04", "x07", "n11", "k05",
                      "n12", "x08", "k06", "n13", "x09", "n14"])
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
    router2(d, lf, 960, 800, 0.75, led=("green" if (lf % 40) < 20 else "red"))
    xargoth2(d, lf, 620, 700 - bA, 0.85, emotion="panic", pose="phone")
    cat2(d, lf, 1300, 760 - bB, 0.8, pose="loaf", sparkle=True)
    txt(d, (620, 470), "圏外", F(52, True, True), REDC, anchor="mm", stroke=3, sfill=INK)
    for i in range(3):
        on = math.sin(lf / 6 - i * 1.2) > 0
        d.ellipse([890 + (i - 1) * 70 - 16, 178, 890 + (i - 1) * 70 + 16, 210],
                  fill=ACCENT if on else blend(CREAM, ACCENT, 0.25), outline=INK, width=5)
    txt(d, (960, 96), "Ａパート終了", F(72, True, True), INK, anchor="mm")
    txt(d, (960, 930), "SEE YOU AFTER THE BREAK!", F(54), ACCENT, anchor="mm",
        stroke=2, sfill=INK)
    return cam_apply(img, 0, 0, 1)


# ###PART2###

# ============================ B-PART ============================
def seg_bpart(g):
    lf = g - OFF_F["bpart"]
    img = Image.new("RGB", (DW, DH), TM_WALL)
    d = ImageDraw.Draw(img)
    sil0f, sil1f = int(E["payday_silence"][0] * FPS), int(E["payday_silence"][1] * FPS)
    frozen = sil0f <= g <= sil1f
    fz = sil0f if frozen else g  # freeze the world during the silence beat

    tastymart2(d, g)
    wifi_sign(d, 480, 210, 1.0, dead=(g >= int(E["snipe_t"] * FPS)), f=g)
    microwave2(d, 1720, 500, 1.0, open_=(g >= int(E["micro_t"] * FPS)), f=fz)

    if lf < 750:  # ---- B1 the receipt password ----
        # crown merchandise + last pudding on the counter
        crown2(d, 1450, 470, 0.8, glow=(lf % 80 < 40), f=fz)
        d.rounded_rectangle([1240, 500, 1330, 560], 6, fill=(250, 210, 120),
                            outline=INK, width=4)
        txt(d, (1285, 530), "LAST", F(22, True, False), TM_RED, anchor="mm")
        xargoth2(d, fz, 1600, 470, 1.05, emotion="smug",
                 talking=talking("x", g),
                 pose=("present" if 220 <= lf < 420 else "idle"), cap=True, apron=True)
        minor_person(d, fz, 1230, 560, 1.02, shirt=TM_GREEN,
                     talking=talking("m", g), flip=True, cap_color=TM_RED)
        kenji2(d, fz, 430, 690, 1.0, panic=False, talking=talking("k", g),
               prop=("point" if 380 <= lf < 540 else "none"))
        if 380 <= lf < 540:  # couch coins
            for i in range(5):
                a = math.radians(200 + i * 22)
                cxx = 560 + math.cos(a) * (50 + i * 8)
                cyy = 640 + math.sin(a) * 26
                d.ellipse([cxx - 12, cyy - 12, cxx + 12, cyy + 12],
                          fill=CROWN, outline=INK, width=3)
        # the receipt reveal
        n16_f = line_window("n16")[0]
        if g >= n16_f - 6:
            receipt2(d, 960, 330, 1.35, show_pass=True, f=fz - n16_f + 6)
            for i in range(2):
                r = 60 + i * 40
                d.arc([960 - r, 330 - r, 960 + r, 330 + r], -60, 60,
                      fill=CROWN, width=6)
        cat2(d, fz, 250, 750, 0.75, pose="loaf")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
    elif lf < 1410:  # ---- B2 the auction rises / microwave war ----
        l2 = lf - 750
        # the listing: crown on a pedestal, weeping
        crown2(d, 960, 400, 1.5, glow=True, tears=True, f=fz)
        d.polygon([(820, 560), (1100, 560), (1060, 640), (860, 640)],
                  fill=blend(TM_WALL, INK, 0.3), outline=INK, width=6)
        d.rounded_rectangle([810, 200, 1110, 260], 8, fill=CREAM, outline=INK, width=5)
        txt(d, (960, 230), "NOW LIVE: CURSED CROWN", F(28, True, False), INK, anchor="mm")
        # bid board rises
        bids = [(line_window("n17")[0], 80000), (line_window("c01")[0], 120000),
                (line_window("n18")[0], 150000)]
        b0, bv = 0, 0
        for tf, vv in bids:
            if g >= tf:
                b0, bv = tf, vv
        if bv:
            bid_board(d, fz, 1560, 240, 1.0, bid=bv, t=(g - b0) / 9)
        # customer browsing
        if l2 < 400:
            minor_person(d, fz, 600, 560, 1.02, shirt=(200, 130, 70),
                         talking=talking("c", g), flip=True)
            d.ellipse([560, 380, 600, 420], outline=(220, 130, 60), width=5)
            txt(d, (660, 400), "?", F(56), (220, 130, 60), anchor="mm")
        xargoth2(d, fz, 1600, 470, 1.05,
                 emotion=("menace" if g >= int(E["micro_t"] * FPS) - 60 else "smug"),
                 talking=talking("x", g),
                 pose=("fist" if g >= int(E["micro_t"] * FPS) else "idle"),
                 cap=True, apron=True)
        if g >= int(E["micro_t"] * FPS):
            speedlines(d, fz, blend(TM_WALL, REDC, 0.4), 0.4, cx=1600, cy=380)
            txt(d, (1600, 250), "宣戦布告", F(80, True, True), CREAM,
                anchor="mm", stroke=5, sfill=REDC)
        kenji2(d, fz, 300, 600, 1.02, panic=True, talking=talking("k", g),
               prop=("mop" if g < line_window("k09")[0] else "none"))
        # onigiri union protest
        k09f = line_window("k09")[0]
        if g >= k09f:
            for i in range(3):
                onigiri(d, 700 + i * 70, 560, 0.9)
            d.rectangle([688, 480, 906, 522], fill=CREAM, outline=INK, width=4)
            txt(d, (797, 501), "ONIGIRI UNION", F(24, True, False), INK, anchor="mm")
        cat2(d, fz, 250, 750, 0.75, pose="loaf")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
    elif lf < 2100:  # ---- B3 the snipe + silence ----
        l3 = lf - 1410
        bid_t = int(E["bid_t"] * FPS)
        snipe_t = int(E["snipe_t"] * FPS)
        crown2(d, 960, 400, 1.5, glow=(g < snipe_t), tears=True, f=fz)
        d.polygon([(820, 560), (1100, 560), (1060, 640), (860, 640)],
                  fill=blend(TM_WALL, INK, 0.3), outline=INK, width=6)
        bid_board(d, fz, 1560, 240, 1.0,
                  bid=(238000 if g >= bid_t else 150000), t=1.0)
        # characters through the whole sequence
        if g < bid_t:  # the stakeout (m02/x14/n19)
            xargoth2(d, fz, 1300, 520, 1.04, emotion="menace", pose="hide",
                     cap=True, apron=True)
            kenji2(d, fz, 400, 640, 1.02, panic=False, prop="mop")
        elif g < snipe_t:  # countdown
            remain = max(0, int(round(60 * (1 - (g - bid_t) / max(1, snipe_t - bid_t)))))
            puls = 1 + 0.12 * math.sin(lf / 2)
            txt(d, (860, 180), "{:02d}".format(remain), F(int(120 * puls), True, False),
                CREAM if remain > 10 else ACCENT, anchor="mm", stroke=6, sfill=INK)
            txt(d, (860, 270), "SECONDS", F(28, False, False), blend(CREAM, INK, 0.7),
                anchor="mm")
            kenji2(d, fz, 400, 620, 1.02, panic=True, prop="none")
            xargoth2(d, fz, 1400, 470, 1.06, emotion="awe", pose="formal",
                     cap=True, apron=True)
        elif g < line_window("k11")[1] + 10:  # the drop + despair
            xargoth2(d, fz, 1400, 500, 1.06, emotion="panic", pose="hide",
                     cap=True, apron=True)
            kenji2(d, fz, 400, 640, 1.02, panic=True, prop="facepalm")
        else:  # the deadpan verdict
            xargoth2(d, g, 1400, 490, 1.06, emotion="smug", pose="formal",
                     cap=True, apron=True)
            kenji2(d, g, 400, 640, 1.02, panic=False, prop="facepalm")
        if snipe_t <= g < snipe_t + 22:  # the drop
            static_fx(d, g, snipe_t, 0.9)
        if g >= snipe_t:
            stamp(d, g, snipe_t + 14, "AUCTION ENDED", "connection lost")
            wifi_sign(d, 480, 210, 1.0, dead=True, f=g)
            d.rounded_rectangle([1240, 500, 1330, 560], 6, fill=blend((250, 210, 120), INK, 0.5),
                                outline=INK, width=4)
        cat2(d, fz, 250, 750, 0.75, pose="loaf")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        frame = vignette(frame, 0.35) if frozen else frame
        dd = ImageDraw.Draw(frame)
    else:  # ---- B4 the buyer ----
        l4 = lf - 2100
        obaa_t = int(E["obaa_t"] * FPS)
        deal_t = int(E["deal_t"] * FPS)
        obx = lerp(2150, 1720, ease_out(prog(g, obaa_t - 30, obaa_t + 10)))
        doom = g >= obaa_t
        if doom:
            obaa2(d, fz, obx, 620, 0.98, doom=True, talking=talking("o", g))
            menace(d, fz, 1450, 240, ["ゴ", "ゴ", "ゴ"], CROWN, TM_WALL, size=58)
        crown2(d, 1450, 470, 0.8, glow=(g < deal_t), f=fz)
        # crown delivery arc at the deal
        if deal_t <= g < deal_t + 30:
            tt = (g - deal_t) / 30
            cx2 = lerp(1450, 1150, ease_out(tt))
            cy2 = 470 - math.sin(tt * math.pi) * 260
            crown2(d, cx2, cy2, 0.85, glow=True, f=g)
        elif g >= deal_t + 30:
            crown2(d, 1150, 300, 0.6, glow=True, f=fz)
            d.polygon([(1120, 330), (1180, 330), (1170, 360), (1130, 360)],
                      fill=blend(TM_WALL, INK, 0.2), outline=INK, width=4)
        # money travels in a circle: Obaa → Xargoth → rent tray
        if g >= deal_t + 20:
            ph = ((g - deal_t - 20) % 60) / 60
            if ph < 0.5:
                mx = lerp(1720, 1150, ease_io(ph * 2))
                my = 560 - math.sin(ph * 2 * math.pi) * 120
            else:
                mx = lerp(1150, 1450, ease_io((ph - 0.5) * 2))
                my = 540 - math.sin((ph - 0.5) * 2 * math.pi) * 100
            d.rounded_rectangle([mx - 46, my - 30, mx + 46, my + 30], 5,
                                fill=PAPER, outline=INK, width=4)
            d.line([mx - 46, my - 30, mx, my + 8, mx + 46, my - 30][0:2], fill=INK, width=3)
            d.line([mx - 46, my - 30, mx, my + 8], fill=INK, width=3)
            d.line([mx + 46, my - 30, mx, my + 8], fill=INK, width=3)
            txt(d, (mx, my - 4), "¥", F(26, True, False), ACCENT, anchor="mm")
        xemo = "panic" if doom else "panic"
        xpose = "kneel" if doom else "hide"
        if g >= line_window("x16")[0]:
            xpose = "formal"
        xargoth2(d, fz, 1150, 540, 1.05, emotion=("smug" if xpose == "formal" else "panic"),
                 talking=talking("x", g), pose=xpose)
        kenji2(d, fz, 430, 640, 1.0, panic=doom, prop=("facepalm" if not doom else "none"))
        cat2(d, fz, 250, 750, 0.75, pose="loaf")
        if l4 >= 540:
            txt(d, (960, 830), "つづく", F(72, True, True), CREAM, anchor="mm",
                stroke=4, sfill=INK)
        if l4 >= 570:
            txt(d, (960, 930), "meow.", F(40, False), HALO, anchor="mm")
        frame = cam_apply(img, 0, 0, 1)
        dd = ImageDraw.Draw(frame)
        frame = vignette(frame, 0.3) if doom else frame
        dd = ImageDraw.Draw(frame)
    # subtitles + dons + wipes + laughs
    dd = ImageDraw.Draw(frame)
    for w0 in (742, 1402, 2092):
        draw_wipe(dd, g, OFF_F["bpart"] + w0)
    don(dd, g, OFF_F["bpart"] + 900, 1550, 300, K)
    don(dd, g, OFF_F["bpart"] + 1140, 960, 260, K)
    for lt in E["laugh_t"][4:6]:
        laugh(dd, g, int(lt * FPS), K, 26)
    sub_frame(g, dd, ["n15", "m01", "x10", "k08", "n16", "x11",
                      "n17", "c01", "x12", "k09", "n18", "x13",
                      "m02", "x14", "n19", "k10", "n20", "x15", "k11",
                      "n21", "o01", "o02", "x16"])
    return frame


# ============================ END CARD ============================
def seg_end(g):
    lf = g - OFF_F["end"]
    img = Image.new("RGB", (DW, DH), INK)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 90, 1830, 990], 20, outline=blend(INK, CREAM, 0.4), width=6)
    if lf > 8:
        txt(d, (960, 170), "NEXT EPISODE", F(56), HALO, anchor="mm")
    txt(d, (960, 280), "第三話「魔王、深夜勤務」", F(78, True, True), CREAM, anchor="mm")
    txt(d, (960, 370), "Ep. 3 — “Demon Lord, Night Shift”", F(38, False),
        (184, 169, 208), anchor="mm")
    # the router, redeemed, green at last
    router2(d, lf, 960, 640, 1.0, led="green", glow=True)
    d.polygon([(880, 700), (1040, 700), (1010, 760), (910, 760)],
              fill=blend(INK, CREAM, 0.12), outline=CREAM, width=4)
    # the lease reveal (page nine) while Kenji screams
    if 30 <= lf < 160:
        lease_folder(d, 400, 620, 0.95, t=(lf - 30) / 9, page9=True)
    # the cat exits with the pudding
    catX = lerp(-260, 2150, ease_io(min(1, max(0, (lf - 240) / 110))))
    cat2(d, g, catX, 940, 0.7, pose="loaf")
    d.polygon([(catX - 20, 940 + 18), (catX + 20, 940 + 18), (catX + 12, 940 + 44),
               (catX - 12, 940 + 44)], fill=(250, 210, 120), outline=INK, width=3)
    if lf > 150:
        txt(d, (960, 700), "DEMON LORD, PAY RENT! — Episode 2", F(36, False),
            blend(INK, CREAM, 0.9), anchor="mm")
    frame = cam_apply(img, 0, 0, 1)
    dd = ImageDraw.Draw(frame)
    sub_frame(g, dd, ["x16", "n21", "o02", "k12", "x17", "n22"])
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
