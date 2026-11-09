#!/usr/bin/env python3
"""DLPR Ep2 props — router, cursed crown, receipt, note, bid board, microwave,
lease folder, static/zap FX, countdown, stamp. Design space 1920x1080."""
import math
from dlpr_common import (
    INK, CREAM, PAPER, WALL, LAMP, ACCENT, FIRE, WHITE, REDC, CROWN, GOLD,
    HALO, LED_G, LED_R, TM_RED, TM_GREEN, TM_SHELF, CFUR, FLOOR,
    blend, pop, ease_out, ease_io, txt, F, K,
)


def router2(d, f, x, y, sc=1.0, led="red", glow=False, cable=True):
    """The router — body, two antennas, LED, ethernet cable. led: red|green|off."""
    P = lambda dx, dy: (x + dx * sc, y + dy * sc)
    lw = lambda w: max(2, int(w * sc))
    if glow:
        pul = 0.5 + 0.3 * math.sin(f / 6)
        d.ellipse([P(-170, -130)[0], P(-170, -130)[1], P(170, 130)[0], P(170, 130)[1]],
                  fill=blend(FLOOR, CROWN, 0.22 * pul))
    # ethernet cable to the left
    if cable:
        pts = []
        for i in range(9):
            tt = i / 8
            pts.append((P(-60 - tt * 260, 18 + math.sin(f / 9 + tt * 3) * 8 + tt * 26)[0],
                        P(-60 - tt * 260, 18 + math.sin(f / 9 + tt * 3) * 8 + tt * 26)[1]))
        d.line(pts, fill=INK, width=lw(7))
    # body
    d.rounded_rectangle([P(-110, -28)[0], P(-28, -28)[1], P(110, 28)[0], P(28, 28)[1]],
                        10, fill=(56, 56, 72), outline=INK, width=lw(5))
    d.rounded_rectangle([P(-96, -16)[0], P(-16, -16)[1], P(40, 16)[0], P(16, 16)[1]],
                        6, fill=(72, 72, 92), outline=INK, width=lw(2))
    # antennas
    for ax, tilt in ((-70, -14), (70, 12)):
        x0, y0 = P(ax, -28)
        x1, y1 = P(ax + tilt, -92)
        d.line([x0, y0, x1, y1], fill=(40, 40, 52), width=lw(8))
        d.ellipse([x1 - 6 * sc, y1 - 6 * sc, x1 + 6 * sc, y1 + 6 * sc],
                  fill=(40, 40, 52), outline=INK, width=lw(2))
    col = {"red": LED_R, "green": LED_G, "off": (90, 60, 60)}[led]
    blink = led == "red" and (f % 46) < 8
    c = col if not blink else blend(col, (20, 10, 10), 0.75)
    d.ellipse([P(84, -10)[0], P(-10, -10)[1], P(104, 10)[0], P(10, 10)[1]],
              fill=c, outline=INK, width=lw(2))
    if led == "green" and (f % 30) < 20:
        for i in range(2):
            r0 = 18 + i * 14 + (f % 30) * 0.6
            d.arc([P(94 - r0, -r0)[0], P(-r0, -r0)[1], P(94 + r0, r0)[0], P(r0, r0)[1]],
                  -60, 60, fill=LED_G, width=lw(3))
    txt(d, P(0, 44), "OBAA-NET 302", F(20 * sc, False), blend(CREAM, INK, 0.65), anchor="mm")


def crown2(d, x, y, sc=1.0, glow=False, tears=False, f=0):
    """The cursed crown — for sale. Optionally weeping."""
    P = lambda dx, dy: (x + dx * sc, y + dy * sc)
    if glow:
        pul = 0.5 + 0.3 * math.sin(f / 5)
        d.ellipse([P(-150, -120)[0], P(-150, -120)[1], P(150, 120)[0], P(150, 120)[1]],
                  fill=blend(FLOOR, CROWN, 0.30 * pul))
    d.polygon([P(-70, 30), P(-70, -30), P(-46, 6), P(-24, -48), P(0, 4),
               P(24, -48), P(46, 6), P(70, -30), P(70, 30)],
              fill=CROWN, outline=INK, width=max(2, int(6 * sc)))
    d.rectangle([P(-70, 22)[0], P(22, 22)[1], P(70, 46)[0], P(46, 46)[1]],
                fill=CROWN, outline=INK, width=max(2, int(5 * sc)))
    for gx in (-38, 38):
        d.ellipse([P(gx - 8, -2)[0], P(-2, -2)[1], P(gx + 8, 14)[0], P(14, 14)[1]],
                  fill=FIRE, outline=INK, width=max(2, int(3 * sc)))
    d.ellipse([P(-10, -30)[0], P(-30, -30)[1], P(10, -10)[0], P(-10, -10)[1]],
              fill=REDC, outline=INK, width=max(2, int(3 * sc)))
    if tears:
        for i, tx in enumerate((-52, 0, 52)):
            tt = ((f / 26) + i * 0.33) % 1
            ty = 46 + tt * 60
            d.polygon([P(tx - 6, ty), P(tx + 6, ty), P(tx, ty + 16)], fill=(127, 212, 255),
                      outline=INK, width=max(1, int(2 * sc)))


def receipt2(d, x, y, sc=1.0, show_pass=True, f=0):
    P = lambda dx, dy: (x + dx * sc, y + dy * sc)
    wp = 0.7 + 0.3 * pop(min(1, max(0, f)))
    s = sc * wp
    P2 = lambda dx, dy: (x + dx * s, y + dy * s)
    d.polygon([P2(-80, -110), P2(80, -110), P2(72, 130), P2(64, 118), P2(56, 130),
               P2(48, 118), P2(40, 130), P2(-64, 130), P2(-72, 118), P2(-80, 130)],
              fill=CREAM, outline=INK, width=max(2, int(5 * s)))
    txt(d, P2(0, -78), "TASTY MART", F(26 * s, True, False), INK, anchor="mm")
    d.line([P2(-56, -60)[0], P2(-56, -60)[1], P2(56, -60)[0], P2(56, -60)[1]],
           fill=INK, width=max(2, int(2 * s)))
    txt(d, P2(0, -36), "LIMITED PUDDING", F(18 * s, False, False), INK, anchor="mm")
    txt(d, P2(0, -8), "YEN 130", F(24 * s, True, False), ACCENT, anchor="mm")
    d.line([P2(-56, 12)[0], P2(-56, 12)[1], P2(56, 12)[0], P2(56, 12)[1]],
           fill=INK, width=max(2, int(2 * s)))
    if show_pass:
        txt(d, P2(0, 40), "Wi-Fi PASS", F(16 * s, False, False),
            blend(CREAM, INK, 0.6), anchor="mm")
        txt(d, P2(0, 74), "obaa0302", F(30 * s, True, False), INK, anchor="mm")
    txt(d, P2(0, 106), "THANK YOU / ありがとう", F(14 * s, False, True),
        blend(CREAM, INK, 0.55), anchor="mm")


def note2(d, x, y, sc=1.0, t=1.0):
    """The landlady's note."""
    s = sc * (0.7 + 0.3 * pop(min(1, max(0, t))))
    P = lambda dx, dy: (x + dx * s, y + dy * s)
    d.polygon([P(-110, -60), P(110, -52), P(102, 58), P(-102, 66)],
              fill=PAPER, outline=INK, width=max(2, int(5 * s)))
    txt(d, P(0, -20), "Wi-Fi resumes", F(30 * s, True, False), INK, anchor="mm")
    txt(d, P(0, 22), "when rent does.", F(30 * s, True, False), ACCENT, anchor="mm")


def bid_board(d, f, x, y, sc=1.0, bid=0, t=1.0):
    """Auction bid overlay panel."""
    s = sc * (0.7 + 0.3 * pop(min(1, max(0, t))))
    P = lambda dx, dy: (x + dx * s, y + dy * s)
    d.rounded_rectangle([P(-230, -80)[0], P(-80, -80)[1], P(230, 80)[0], P(80, 80)[1]],
                        14, fill=INK, outline=CROWN, width=max(2, int(6 * s)))
    txt(d, P(0, -40), "CURRENT BID", F(24 * s, False, False), CREAM, anchor="mm")
    hot = bid >= 238000
    col = CROWN if hot else LED_G
    txt(d, P(0, 14), "¥{:,.0f}".format(bid), F(52 * s, True, False), col,
        anchor="mm", stroke=2, sfill=INK)
    if hot:
        txt(d, P(0, 58), "EXACT TO THE YEN", F(20 * s, True, False), ACCENT, anchor="mm")


def microwave2(d, x, y, sc=1.0, open_=False, f=0):
    P = lambda dx, dy: (x + dx * sc, y + dy * sc)
    lw = lambda w: max(2, int(w * sc))
    d.rounded_rectangle([P(-120, -90)[0], P(-90, -90)[1], P(120, 90)[0], P(90, 90)[1]],
                        8, fill=(150, 156, 168), outline=INK, width=lw(5))
    if open_:
        d.polygon([P(-118, -86), P(-40, -86), P(-70, -160), P(-140, -152)],
                  fill=(120, 126, 138), outline=INK, width=lw(4))
        for i in range(3):
            r = 30 + i * 26 + (f % 18) * 1.2
            d.arc([P(-10 - r, -r)[0], P(-r, -r)[1], P(-10 + r, r)[0], P(r, r)[1]],
                  -30, 30, fill=blend(CREAM, INK, 0.5), width=lw(3))
    else:
        d.rounded_rectangle([P(-100, -70)[0], P(-70, -70)[1], P(30, 70)[0], P(70, 70)[1]],
                            6, fill=(60, 58, 70), outline=INK, width=lw(4))
        d.ellipse([P(-70, -40)[0], P(-40, -40)[1], P(0, 0)[0], P(0, 0)[1]],
                  outline=blend(CREAM, INK, 0.3), width=lw(2))
    d.rounded_rectangle([P(46, -60)[0], P(-60, -60)[1], P(102, 40)[0], P(40, 40)[1]],
                        4, fill=(230, 120, 60), outline=INK, width=lw(3))
    txt(d, P(74, -10), "60", F(26 * sc, True, False), INK, anchor="mm")
    d.rectangle([P(-100, 58)[0], P(58, 58)[1], P(100, 78)[0], P(78, 78)[1]],
                fill=TM_RED, outline=INK, width=lw(2))
    txt(d, P(-2, 68), "NuNu-2000", F(14 * sc, False, False), WHITE, anchor="mm")


def wifi_sign(d, x, y, sc=1.0, dead=False, f=0):
    P = lambda dx, dy: (x + dx * sc, y + dy * sc)
    lw = lambda w: max(2, int(w * sc))
    d.line([P(-120, -80), P(-110, -10)], fill=INK, width=lw(4))
    d.line([P(120, -80), P(110, -10)], fill=INK, width=lw(4))
    d.rounded_rectangle([P(-130, -10)[0], P(-10, -10)[1], P(130, 50)[0], P(50, 50)[1]],
                        8, fill=CREAM if not dead else blend(CREAM, INK, 0.35),
                        outline=INK, width=lw(4))
    col = TM_GREEN if not dead else LED_R
    txt(d, P(0, 20), "FREE Wi-Fi", F(34 * sc, True, False), col, anchor="mm")
    if not dead:
        for i in range(3):
            r = 16 + i * 16 + (f % 22) * 0.5
            d.arc([P(96 - r, 30 - r)[0], P(30 - r, 30 - r)[1], P(96 + r, 30 + r)[0],
                   P(30 + r, 30 + r)[1]], -60, 60, fill=col, width=lw(2))


def lease_folder(d, x, y, sc=1.0, t=1.0, page9=False):
    s = sc * (0.7 + 0.3 * pop(min(1, max(0, t))))
    P = lambda dx, dy: (x + dx * s, y + dy * s)
    d.rounded_rectangle([P(-150, -100)[0], P(-100, -100)[1], P(150, 100)[0], P(100, 100)[1]],
                        8, fill=(150, 106, 66), outline=INK, width=max(2, int(6 * s)))
    d.rectangle([P(-150, -30)[0], P(-30, -30)[1], P(150, -6)[0], P(-6, -6)[1]],
                fill=CREAM, outline=INK, width=max(2, int(3 * s)))
    txt(d, P(0, -18), "LEASE — ROOM 302", F(22 * s, True, False), INK, anchor="mm")
    if page9:
        d.rounded_rectangle([P(20, -90)[0], P(-90, -90)[1], P(142, 92)[0], P(92, 92)[1]],
                            4, fill=CREAM, outline=INK, width=max(2, int(4 * s)))
        txt(d, P(80, -60), "P.9 AMENITIES", F(16 * s, False, False),
            blend(CREAM, INK, 0.6), anchor="mm")
        txt(d, P(80, -10), "Wi-Fi:", F(20 * s, False, False), INK, anchor="mm")
        txt(d, P(80, 28), "obaa0302", F(30 * s, True, False), ACCENT, anchor="mm")
        d.line([P(30, 52)[0], P(52, 52)[1], P(132, 52)[0], P(132, 52)[1]],
               fill=blend(CREAM, INK, 0.4), width=max(2, int(2 * s)))
        d.line([P(30, 74)[0], P(74, 74)[1], P(132, 74)[0], P(132, 74)[1]],
               fill=blend(CREAM, INK, 0.4), width=max(2, int(2 * s)))


def zap(d, f, t0, x, y, dur=12):
    t = f - t0
    if t < 0 or t > dur:
        return
    for i in range(5):
        a = math.radians(i * 72 + t * 30)
        r0 = 20 + t * 6
        r1 = r0 + 60 - t * 4
        d.line([x + math.cos(a) * r0, y + math.sin(a) * r0,
                x + math.cos(a) * r1, y + math.sin(a) * r1],
               fill=(255, 240, 160) if i % 2 == 0 else WHITE, width=6)
    d.ellipse([x - 18, y - 18, x + 18, y + 18], outline=WHITE, width=4)


def static_fx(d, f, t0, intensity=1.0, dur=14):
    t = f - t0
    if t < 0 or t > dur:
        return
    k = (1 - t / dur) * intensity
    n = int(26 * k)
    for i in range(n):
        yy = (i * 97 + t * 331) % 1080
        xx = ((i * 313 + t * 547) % 400) - 200
        wdt = max(2, int(6 * k))
        d.rectangle([xx, yy, xx + 1920 + 400, yy + wdt],
                    fill=blend(CREAM, INK, 0.5) if i % 2 else (160, 160, 180))


def stamp(d, f, t0, word, sub, x=960, y=430):
    t = f - t0
    if t < 0 or t > 40:
        return
    s = 1.6 - 0.6 * min(1, t / 5)
    a = -8
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))

    def R(dx, dy):
        return (x + (dx * ca - dy * sa) * s, y + (dx * sa + dy * ca) * s)
    pts = [R(-330, -90), R(330, -90), R(330, 90), R(-330, 90)]
    d.polygon(pts, outline=REDC, width=max(3, int(10 * s)))
    d.polygon([R(-318, -78), R(318, -78), R(318, 78), R(-318, 78)], outline=REDC,
              width=max(2, int(4 * s)))
    txt(d, R(0, -18), word, F(76 * s, True, False), REDC, anchor="mm")
    txt(d, R(0, 42), sub, F(26 * s, False, False), REDC, anchor="mm")
