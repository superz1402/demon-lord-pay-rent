#!/usr/bin/env python3
"""DLPR Ep1 FULL renderer — shared drawing library (characters v2, sets, FX).

Design space 1920x1080, output 1280x720 (K=2/3 downsample = antialiasing).
Reads timeline.json for narration windows (mouth flaps + beats).
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
FPS = TL["fps"]
TOTAL_F = TL["total_frames"]
EVENTS = TL["events"]

W, H = 1280, 720
DW, DH = 1920, 1080
K = W / DW

# ---------------- palette ----------------
INK=(29,22,38); CREAM=(255,246,229); PAPER=(247,232,201); WALL=(74,59,99)
WALL_D=(58,45,80); FLOOR=(43,33,56); LAMP=(255,182,92); WINC=(26,36,64)
XSKIN=(159,223,182); XSKIN_D=(120,190,150); XCAPE=(91,42,134); XCAPE_D=(64,28,100)
XCAPE_L=(122,68,176); XHAIR=(42,18,64); XHAIR_L=(80,38,118); CROWN=(245,197,66)
KHOOD=(62,124,177); KHOOD_D=(44,96,140); KHAIR=(46,42,50); KSKIN=(243,200,158)
KSKIN_D=(214,168,124); CFUR=(242,233,220); CFUR_D=(214,198,178)
CPATCH=(232,135,74); HALO=(255,224,102); ACCENT=(255,90,78)
FIRE=(180,92,255); WHITE=(255,255,255); REDC=(192,57,43)
SOFA=(122,78,140); SOFA2=(138,92,158); SOFA3=(154,108,174)
TABLE=(176,122,74); TABLE2=(138,92,56); CURT=(110,43,94)
OB_SKIN=(243,214,182); OB_CARD=(94,74,120); OB_APRON=(232,220,192)
OB_HAIR=(207,203,216); GOLD=(245,197,66)
TM_WALL=(38,52,74); TM_FLOOR=(30,38,56); TM_SHELF=(196,150,96)
TM_GREEN=(46,140,86); TM_RED=(214,64,58); LED_G=(76,224,160); LED_R=(255,59,48)
LAUGHY=(255,210,63); SKYB=(201,162,39); SKYB2=(232,197,88)

FB="/usr/share/fonts/truetype/chinese/NotoSansSC-Bold.ttf"
FR="/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf"
DB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_fc={}
def F(sz, bold=True, jp=False):
    sz=max(8,int(sz))
    key=(sz,bold,jp)
    if key not in _fc:
        p = (FB if bold else FR) if jp else (DB if bold else DR)
        _fc[key]=ImageFont.truetype(p,sz)
    return _fc[key]

def blend(c1,c2,t): return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))
def clamp(v,a,b): return max(a,min(b,v))
def prog(f,a,b): return clamp((f-a)/(b-a),0,1) if b>a else 1.0
def lerp(a,b,t): return a+(b-a)*t
def ease_out(t): return 1-(1-t)**3
def ease_io(t): return 4*t*t*t if t<0.5 else 1-((-2*t+2)**3)/2
def pop(t):
    t=clamp(t,0,1)
    return 1+2.70158*((t-1)**3)+1.70158*((t-1)**2)
def shake(f,amp=3): return amp*math.sin(f/1.7), amp*math.cos(f/2.3)

def txt(d,xy,s,font,fill,anchor="la",stroke=0,sfill=INK):
    d.text(xy,s,font=font,fill=fill,anchor=anchor,
           stroke_width=int(stroke),stroke_fill=sfill)

def txt_shadow(d,xy,s,font,fill,anchor="la",shadow=(0,0),scol=INK):
    d.text((xy[0]+shadow[0],xy[1]+shadow[1]),s,font=font,fill=scol,anchor=anchor)
    d.text(xy,s,font=font,fill=fill,anchor=anchor)

# ---------------- narration / talking windows ----------------
VOICE_BY_CHAR={"n":"n","x":"x","k":"k","m":"m","c":"c","o":"o"}
_TALK={}  # voice -> [(f0,f1)] absolute frames
for L in TL["lines"]:
    _TALK.setdefault(L["voice"],[]).append((L["start"]*FPS, L["end"]*FPS))

def talking(voice, g):
    for f0,f1 in _TALK.get(voice,()):
        if f0-2 <= g <= f1+3: return True
    return False

def line_window(lid):
    for L in TL["lines"]:
        if L["id"]==lid: return L["start"]*FPS, L["end"]*FPS
    return (0,0)

def subtitle(d,g,lid,speaker,color,en,jp=None,cat=False):
    """Rich subtitle bar — drawn on the OUTPUT frame (K-scaled design coords)."""
    s0,s1 = line_window(lid)
    if not (s0-2 <= g <= s1+2): return
    kk=min(1,(g-s0)/6)
    y0,y1=906,1024
    L=lambda v:v*K
    d.rounded_rectangle([L(260),L(y0+6),L(1660),L(y1+6)],L(14),fill=blend(CREAM,INK,0.85))
    d.rounded_rectangle([L(260),L(y0),L(1660),L(y1)],L(14),fill=blend(CREAM,INK,0.82))
    d.rounded_rectangle([L(260),L(y0),L(276),L(y1)],L(8),fill=color)
    if cat:
        d.ellipse([L(306),L(y0+22),L(354),L(y0+70)],fill=CFUR,outline=INK,width=2)
        d.polygon([L(312),L(y0+34),L(318),L(y0+22),L(324),L(y0+34)],fill=CFUR)
        d.polygon([L(336),L(y0+34),L(342),L(y0+22),L(348),L(y0+34)],fill=CFUR)
        txt(d,(L(330),L(y0+46)),"·ᴥ·",F(16*K),INK,anchor="mm")
        sx=L(372)
    else:
        sx=L(306)
    txt_shadow(d,(sx,L(y0+8)),speaker,F(38*K),color,shadow=(2,2))
    txt(d,(sx,L(y0+50)),en,F(31*K,False),WHITE)
    if jp: txt(d,(L(1620),L(y0+8)),jp,F(28*K,True,True),blend(CREAM,color,0.9),anchor="ra")

def speedlines(d,f,color,op=0.85,cx=960,cy=540,k=1.0,density=28):
    rot=(f*1.2)%(360/density)
    for i in range(density):
        a=math.radians(i*360/density+rot)
        wdt=max(2,int((26 if i%2==0 else 10)*op*k))
        col=color if i%2==0 else blend(color,INK,0.4)
        d.line([cx+math.cos(a)*260*k,cy+math.sin(a)*260*k,
                cx+math.cos(a)*1500*k,cy+math.sin(a)*1500*k],fill=col,width=wdt)

def menace(d,f,x,y,chars,color=INK,bg=CREAM,k=1.0,size=64):
    for i,c in enumerate(chars):
        t=(f/40+i*0.33)%1
        txt(d,((x+i*58)*k,(y-t*60)*k),c,F(size*k,True,True),
            blend(bg,color,0.9-t*0.5),anchor="ra")

def don(d,f,t0,x,y,k=1.0):
    t=f-t0
    if t<0 or t>22: return
    grow=lerp(0.4,1.25,min(1,t/6)); fade=1 if t<=16 else max(0,1-(t-16)/6)
    cg=blend(WHITE,CROWN,fade); ca=blend(WHITE,ACCENT,fade); ci=blend(WHITE,INK,fade)
    pts=[]
    for i in range(12):
        a1=math.radians(i*30+15); a2=math.radians(i*30+23)
        pts+=[(x*k+math.cos(a1)*150*grow*k, y*k+math.sin(a1)*150*grow*k),
              (x*k+math.cos(a2)*260*grow*k, y*k+math.sin(a2)*260*grow*k),
              (x*k+math.cos(a2+.1)*150*grow*k, y*k+math.sin(a2+.1)*150*grow*k)]
    d.polygon(pts,fill=cg,outline=ci)
    txt(d,(x*k,y*k+26*grow*k),"ドン",F(120*k,True,True),ca,anchor="mm",stroke=int(8*k*grow),sfill=ci)

def laugh(d,g,t0,k=1.0,len_=26):
    t=g-t0
    if t<0 or t>len_: return
    kk=min(min(1,t/5),max(0,(len_-t)/5))
    d.rectangle([0,880*k,DW*k,DH*k],fill=blend(CREAM,LAUGHY,kk))
    d.line([0,880*k,DW*k,880*k],fill=blend(CREAM,INK,kk),width=max(2,int(8*k)))
    for i,h in enumerate(["HA","HA","HA"]):
        txt(d,((i-1)*260*k+960*k,(980-abs(i-1)*34)*k),h,F(96*k,True,False),
            blend(CREAM,INK,kk),anchor="mm")
        _x=(i-1)*260*k+960*k
        d.arc([_x-160*k,900*k,_x+160*k,1010*k],180,360,fill=blend(CREAM,INK,0.75*kk),width=4)

def flash(img,f,t0,len_=8):
    t=f-t0
    if 0<=t<=len_:
        return Image.blend(img,Image.new("RGB",img.size,WHITE),1-t/len_)
    return img

def cam_apply(img,x,y,s):
    if s==1 and x==0 and y==0:
        return img.resize((W,H),Image.BILINEAR)
    vx=(-960-x)/s+960; vy=(-540-y)/s+540
    vx=clamp(vx,0,1920-1920/s); vy=clamp(vy,0,1080-1080/s)
    return img.resize((W,H),Image.BILINEAR,box=(vx,vy,vx+1920/s,vy+1080/s))

def vignette(frame,strength=0.35):
    vig=Image.new("L",(W,H),0); dv=ImageDraw.Draw(vig)
    dv.ellipse([-W*.25,-H*.25,W*1.25,H*1.25],fill=255)
    vig=vig.filter(ImageFilter.GaussianBlur(50))
    dark=Image.new("RGB",(W,H),INK)
    return Image.composite(frame,dark,vig.point(lambda p:int(p*(1-strength)+255*strength*0.35)))

def wipe_bars(g,t0,n_bars=4,dur=8,direction=1):
    """Ink bar-wipe covering screen at scene cuts. Returns True while covering."""
    t=g-t0
    if t<0 or t>dur: return False
    return True

def draw_wipe(d,g,t0,n_bars=4,dur=8):
    t=g-t0
    if t<0 or t>dur: return
    p=ease_io(min(1,t/(dur*0.6)))
    bh=DH/n_bars
    for i in range(n_bars):
        off=-DW+ (2*DW)*p
        y=i*bh
        x0 = off if i%2==0 else -off
        d.rectangle([x0,y,x0+DW,y+bh+2],fill=INK if i%2==0 else blend(INK,XCAPE,0.5))

# ================= CHARACTERS v2 =================
def xargoth2(d,f,cx,cy,sc=1.0,emotion="smug",talking=False,pose="idle",
             frozen=False,cap=False,apron=False):
    """XARGOTH v2 — 9 poses, cape flutter, shading, highlight hair."""
    fz=f
    bob=math.sin(fz/14)*4*sc
    crouch = -34*sc if pose in("hide","kneel") else 0
    ox,oy=cx,cy+bob+crouch
    P=lambda x,y:(ox+x*sc,oy+y*sc)
    lw=lambda w:max(2,int(w*sc))
    flap=talking and (fz%6)<3
    # ---- aura (smug/menace) ----
    if emotion=="menace":
        for i,(ax,ay,aw) in enumerate([(-120,-120,26),(90,-140,32),(-30,-170,22)]):
            wav=math.sin(fz/5+i*2)*8
            d.polygon([P(ax+wav,ay),P(ax+aw/2+wav,ay-70),P(ax+aw+wav,ay)],fill=XCAPE_L)
    # ---- cape with rippling hem ----
    hem=[(-95,260)]
    for i in range(7):
        hx=-95+i*(190/6)
        hem.append((hx,260+math.sin(fz/7+i*1.3)*6))
    hem.append((95,260))
    d.polygon([P(*p) for p in hem]+[P(108,150),P(90,50),P(0,18),P(-90,50),P(-108,150)],
              fill=XCAPE,outline=INK,width=lw(5))
    d.polygon([P(-108,150),P(-90,50),P(-60,44),P(-80,150)],fill=XCAPE_D)  # shade
    d.polygon([P(-78,60),P(-46,-14),P(-10,46)],fill=XCAPE,outline=INK,width=lw(4))
    d.polygon([P(78,60),P(46,-14),P(10,46)],fill=XCAPE,outline=INK,width=lw(4))
    # apron over cape (part-time gag)
    if apron:
        d.polygon([P(-52,110),P(52,110),P(66,258),P(-66,258)],fill=OB_APRON,outline=INK,width=lw(4))
        d.line([P(-52,150),P(52,150)],fill=INK,width=lw(2))
    # chest
    d.polygon([P(-44,250),P(-44,96),P(0,70),P(44,96),P(44,250)],fill=XSKIN,outline=INK,width=lw(4))
    d.polygon([P(-44,250),P(-44,96),P(-22,88),P(-30,250)],fill=XSKIN_D)  # shade
    # medallion
    d.ellipse([P(-20,110)[0],P(-20,110)[1],P(20,150)[0],P(20,150)[1]],fill=CROWN,outline=INK,width=lw(3))
    txt(d,P(0,130),"滞",F(26*sc,True,True),INK,anchor="mm")
    # ---- arms by pose ----
    if pose=="idle":
        d.line([P(-70,140),P(-30,120),P(-6,150)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,140),P(30,120),P(6,150)],fill=INK,width=lw(7),joint="curve")
    elif pose=="phone":
        d.line([P(-70,140),P(-80,190),P(-60,220)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,140),P(110,90),P(104,40)],fill=INK,width=lw(7),joint="curve")
        ph1,ph2=P(84,-52),P(124,0)
        d.rounded_rectangle([ph1[0],ph1[1],ph2[0],ph2[1]],6,fill=INK)
        d.rounded_rectangle([ph1[0]+4*sc,ph1[1]+4*sc,ph2[0]-4*sc,ph2[1]-4*sc],4,fill=(40,60,90))
        t=(fz%40)/40
        d.arc([P(94,-38)[0],P(94,-38)[1],P(114,-18)[0],P(114,-18)[1]],0,360*t,fill=WHITE,width=3)
    elif pose=="snap":
        d.line([P(-70,140),P(-30,120),P(-6,150)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,140),P(120,110),P(138,86)],fill=INK,width=lw(7),joint="curve")
        d.ellipse([P(130,74)[0],P(130,74)[1],P(150,94)[0],P(150,94)[1]],fill=XSKIN,outline=INK,width=lw(3))
    elif pose=="point":
        d.line([P(-70,140),P(-30,120),P(-6,150)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,140),P(130,120),P(178,116)],fill=INK,width=lw(7),joint="curve")
        d.ellipse([P(172,108)[0],P(172,108)[1],P(190,126)[0],P(190,126)[1]],fill=XSKIN,outline=INK,width=lw(3))
    elif pose=="present":
        d.line([P(-70,130),P(-120,80),P(-138,30)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,130),P(120,80),P(138,30)],fill=INK,width=lw(7),joint="curve")
        for sx0 in (-150,-138):
            d.ellipse([P(sx0,16)[0],P(sx0,16)[1],P(sx0+22,38)[0],P(sx0+22,38)[1]],fill=XSKIN,outline=INK,width=lw(3))
    elif pose=="hide":
        d.line([P(-60,150),P(-40,180),P(-20,160)],fill=INK,width=lw(6),joint="curve")
        d.line([P(60,150),P(40,180),P(20,160)],fill=INK,width=lw(6),joint="curve")
    elif pose=="kneel":
        d.line([P(-70,200),P(-90,250),P(-70,258)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,200),P(90,250),P(70,258)],fill=INK,width=lw(7),joint="curve")
    elif pose=="formal":
        d.line([P(-70,140),P(-60,200),P(-20,232)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,140),P(60,200),P(20,232)],fill=INK,width=lw(7),joint="curve")
    elif pose=="fist":
        d.line([P(-70,140),P(-100,90),P(-96,50)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,140),P(40,100),P(30,70)],fill=INK,width=lw(7),joint="curve")
        d.ellipse([P(-108,28)[0],P(-108,28)[1],P(-80,56)[0],P(-80,56)[1]],fill=XSKIN,outline=INK,width=lw(3))
    # formal envelope held out
    if pose=="formal":
        e1,e2=P(-26,238),P(26,282)
        d.rounded_rectangle([e1[0],e1[1],e2[0],e2[1]],5,fill=PAPER,outline=INK,width=lw(4))
        d.line([P(-26,238),P(0,262),P(26,238)],fill=INK,width=lw(3))
        txt(d,P(0,266),"家賃",F(15*sc,True,True),ACCENT,anchor="mm")
    # ---- head ----
    hx,hy=ox,oy-60*sc
    HP=lambda x,y:(hx+x*sc,hy+y*sc)
    d.polygon([HP(-105,-10),HP(-125,-95),HP(-70,-165),HP(0,-172),HP(70,-165),HP(125,-95),HP(105,-10),
               HP(60,-60),HP(30,-90),HP(0,-40),HP(-30,-90),HP(-60,-60)],fill=XHAIR,outline=INK,width=lw(4))
    d.polygon([HP(-92,-60),HP(-70,-140),HP(-40,-150),HP(-58,-84)],fill=XHAIR_L)  # highlight band
    d.polygon([HP(38,-140),HP(70,-128),HP(88,-70),HP(62,-84)],fill=XHAIR_L)
    d.polygon([HP(-78,-104),HP(-96,-150),HP(-88,-176),HP(-58,-178),HP(-66,-150),HP(-56,-118)],
              fill=(255,243,220),outline=INK,width=lw(3))
    d.polygon([HP(78,-104),HP(96,-150),HP(88,-176),HP(58,-178),HP(66,-150),HP(56,-118)],
              fill=(255,243,220),outline=INK,width=lw(3))
    cg=lambda x,y:(hx+(10+x)*sc,hy+(-160+y)*sc)
    d.polygon([cg(-26,14),cg(-26,-8),cg(-12,2),cg(0,-14),cg(12,2),cg(26,-8),cg(26,14)],
              fill=CROWN,outline=INK,width=lw(3))
    d.ellipse([cg(-4,-9)[0],cg(-4,-9)[1],cg(6,1)[0],cg(6,1)[1]],fill=ACCENT)
    p1,p2=HP(-64,-58),HP(64,62)
    d.rounded_rectangle([p1[0],p1[1],p2[0],p2[1]],radius=int(40*sc),fill=XSKIN,outline=INK,width=lw(5))
    d.polygon([HP(-64,-6),HP(-92,-20),HP(-62,22)],fill=XSKIN,outline=INK,width=lw(3))
    d.polygon([HP(64,-6),HP(92,-20),HP(62,22)],fill=XSKIN,outline=INK,width=lw(3))
    shut = 64<(fz%72)<68
    panic = emotion=="panic"
    if shut:
        for ex in (-46,18):
            d.arc([HP(ex,-12)[0],HP(ex,-12)[1],HP(ex+28,10)[0],HP(ex+28,10)[1]],200,340,fill=INK,width=lw(5))
    else:
        ry=(20 if panic else 15)*sc
        lidoff=(6 if emotion in("smug","menace") else (-14 if panic else 0))*0.4
        for ex in (-32,32):
            d.ellipse([hx+(ex-15)*sc,hy-2*sc-ry,hx+(ex+15)*sc,hy-2*sc+ry],fill=WHITE,outline=INK,width=lw(4))
            d.ellipse([hx+(ex-6)*sc,hy-2*sc+lidoff*sc-6*sc,hx+(ex+6)*sc,hy-2*sc+lidoff*sc+6*sc],fill=INK)
            d.ellipse([hx+(ex-2)*sc,hy-4*sc+lidoff*sc-2*sc,hx+(ex+2)*sc,hy+0*sc+lidoff*sc+2*sc],fill=WHITE)
        if emotion in("smug","menace"):
            d.line([HP(-50,-12),HP(-16,-4)],fill=INK,width=lw(8))
            d.line([HP(16,-4),HP(50,-12)],fill=INK,width=lw(8))
    if panic:
        d.line([HP(-50,-26),HP(-18,-32)],fill=INK,width=lw(5))
        d.line([HP(18,-32),HP(50,-26)],fill=INK,width=lw(5))
    else:
        d.line([HP(-50,-24),HP(-18,-28)],fill=INK,width=lw(5))
        d.line([HP(18,-28),HP(50,-24)],fill=INK,width=lw(5))
    if flap:
        d.polygon([HP(-22,34),HP(22,34),HP(0,58)],fill=INK)
    elif emotion in("smug","menace"):
        q1,q2=HP(-20,26),HP(24,52)
        d.arc([q1[0],q1[1],q2[0],q2[1]],15,165,fill=INK,width=lw(5))
    elif panic:
        d.ellipse([HP(-14,30)[0],HP(-14,30)[1],HP(14,50)[0],HP(14,50)[1]],fill=INK)
    else:
        d.ellipse([HP(-6,36)[0],HP(-6,36)[1],HP(6,48)[0],HP(6,48)[1]],fill=INK)
    for fx0 in (-10,12):
        d.polygon([HP(fx0,38),HP(fx0+4,46),HP(fx0+8,38)],fill=WHITE)
    if panic:
        d.polygon([HP(74,-40),HP(84,-24),HP(64,-24)],fill=(127,212,255),outline=INK,width=lw(3))
    if emotion=="awe":
        d.ellipse([HP(-90,10)[0],HP(-90,10)[1],HP(-78,22)[0],HP(-78,22)[1]],fill=(127,212,255))
    # TASTY MART cap
    if cap:
        d.polygon([HP(-58,-88),HP(58,-88),HP(70,-56),HP(-70,-56)],fill=TM_GREEN,outline=INK,width=lw(4))
        d.rounded_rectangle([HP(-78,-62)[0],HP(-78,-62)[1],HP(78,-50)[0],HP(78,-50)[1]],4,fill=TM_RED,outline=INK,width=lw(3))


def kenji2(d,f,cx,cy,sc=1.0,talking=False,panic=True,prop="env",frozen=False):
    """KENJI v2 — props: env | bag | none | point | mop | phone. facepalm via prop."""
    fz=f
    shk=math.sin(fz/2.2)*2.5*sc if panic else math.sin(fz/16)*3*sc
    ox,oy=cx,cy+shk
    P=lambda x,y:(ox+x*sc,oy+y*sc)
    lw=lambda w:max(2,int(w*sc))
    flap=talking and (fz%6)<3
    d.polygon([P(-80,260),P(-88,130),P(-60,70),P(0,62),P(60,70),P(88,130),P(80,260)],
              fill=KHOOD,outline=INK,width=lw(5))
    d.polygon([P(-80,260),P(-88,130),P(-60,70),P(-40,66),P(-56,260)],fill=KHOOD_D)
    q1,q2=P(-46,58),P(46,110)
    d.arc([q1[0],q1[1],q2[0],q2[1]],20,160,fill=INK,width=lw(5))
    d.line([P(-14,92),P(-18,130)],fill=INK,width=lw(4))
    d.line([P(14,92),P(18,130)],fill=INK,width=lw(4))
    d.line([P(-40,190),P(40,190)],fill=INK,width=lw(4))
    hx,hy=ox,oy-40*sc
    HP=lambda x,y:(hx+x*sc,hy+y*sc)
    d.polygon([HP(-62,-30),HP(-70,-96),HP(-30,-118),HP(0,-118),HP(30,-118),HP(70,-96),HP(62,-30),
               HP(34,-58),HP(0,-64),HP(-34,-58)],fill=KHAIR,outline=INK,width=lw(4))
    d.polygon([HP(-52,-70),HP(-34,-108),HP(-14,-112),HP(-30,-76)],fill=(70,64,74))
    p1,p2=HP(-52,-66),HP(52,58)
    d.rounded_rectangle([p1[0],p1[1],p2[0],p2[1]],radius=int(30*sc),fill=KSKIN,outline=INK,width=lw(5))
    d.polygon([HP(-44,24),HP(-44,54),HP(-18,54),HP(-26,28)],fill=KSKIN_D)
    if panic:
        d.polygon([HP(40,-66),HP(48,-80),HP(32,-78)],fill=ACCENT)
    shut = 64<(fz%72)<68
    ry=(17 if panic else 13)*sc
    if shut:
        for ex in (-38,14):
            d.arc([HP(ex,-14)[0],HP(ex,-14)[1],HP(ex+24,8)[0],HP(ex+24,8)[1]],200,340,fill=INK,width=lw(4))
    else:
        for ex in (-26,26):
            d.ellipse([hx+(ex-13)*sc,hy-4*sc-ry,hx+(ex+13)*sc,hy-4*sc+ry],fill=WHITE,outline=INK,width=lw(4))
            d.ellipse([hx+(ex-5)*sc,hy-9*sc,hx+(ex+5)*sc,hy+1*sc],fill=INK)
    for ex in (-36,16):
        q1,q2=HP(ex,4),HP(ex+20,18)
        d.arc([q1[0],q1[1],q2[0],q2[1]],20,160,fill=INK,width=lw(3))
    if flap:
        d.ellipse([HP(-16,22)[0],HP(-16,22)[1],HP(16,46)[0],HP(16,46)[1]],fill=INK)
    elif prop=="facepalm":
        d.arc([HP(-12,26)[0],HP(-12,26)[1],HP(12,40)[0],HP(12,40)[1]],200,340,fill=INK,width=lw(4))
    else:
        d.arc([HP(-12,26)[0],HP(-12,26)[1],HP(12,40)[0],HP(12,40)[1]],200,340,fill=INK,width=lw(4))
    # small hope-smile for B3
    if prop=="smile":
        d.arc([HP(-12,26)[0],HP(-12,26)[1],HP(12,40)[0],HP(12,40)[1]],20,160,fill=INK,width=lw(4))
    if prop=="facepalm":
        d.line([P(-70,130),P(-30,60),P(0,10)],fill=INK,width=lw(7),joint="curve")
        d.ellipse([HP(-26,-58)[0],HP(-26,-58)[1],HP(22,-14)[0],HP(22,-14)[1]],fill=KSKIN,outline=INK,width=lw(4))
        d.line([P(70,130),P(80,190),P(60,220)],fill=INK,width=lw(7),joint="curve")
    elif prop=="env":
        d.line([P(-70,130),P(-80,190),P(-60,220)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,130),P(130,110),P(168,96)],fill=INK,width=lw(7),joint="curve")
        e=lambda x,y:(ox+(196+x*math.cos(math.radians(-12))-y*math.sin(math.radians(-12)))*sc,
                      oy+(86+x*math.sin(math.radians(-12))+y*math.cos(math.radians(-12)))*sc)
        d.polygon([e(-46,-30),e(46,-30),e(46,30),e(-46,30)],fill=PAPER,outline=INK)
        d.line([e(-46,-30),e(0,8),e(46,-30)],fill=INK,width=lw(3))
        c0,c1=e(22,4),e(46,28)
        d.ellipse([min(c0[0],c1[0]),min(c0[1],c1[1]),max(c0[0],c1[0]),max(c0[1],c1[1])],fill=ACCENT,outline=INK,width=lw(2))
        txt(d,e(34,16),"家賃",F(15*sc,True,True),WHITE,anchor="mm")
    elif prop=="bag":
        d.line([P(-70,130),P(-80,190),P(-60,220)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,130),P(120,170),P(118,214)],fill=INK,width=lw(7),joint="curve")
        b1,b2=P(70,214),P(166,214)
        d.rounded_rectangle([b1[0],b1[1],b2[0],b2[1]+40],10,fill=(240,240,244),outline=INK,width=lw(4))
        d.arc([b1[0]+16,b1[1]-22,b2[0]-16,b1[1]+14],180,360,fill=INK,width=lw(4))
        for i in range(4):
            d.polygon([P(84+i*20,238+i*0),P(96+i*20,238),P(90+i*20,226)],fill=PAPER,outline=INK,width=2)
        txt(d,P(118,244),"IOU",F(16*sc),INK,anchor="mm")
    elif prop=="point":
        d.line([P(-70,130),P(-80,190),P(-60,220)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,130),P(140,140),P(186,150)],fill=INK,width=lw(7),joint="curve")
        d.ellipse([P(182,142)[0],P(182,142)[1],P(202,162)[0],P(202,162)[1]],fill=KSKIN,outline=INK,width=lw(3))
    elif prop=="mop":
        d.line([P(-70,130),P(-80,190),P(-60,220)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,130),P(96,60),P(150,-60)],fill=INK,width=lw(6),joint="curve")
        d.line([P(150,-60),P(196,-160)],fill=(150,120,80),width=lw(8))
        d.ellipse([P(176,-160)[0],P(176,-160)[1],P(240,-100)[0],P(240,-100)[1]],fill=(230,230,235),outline=INK,width=lw(3))
    elif prop=="phone":
        d.line([P(-70,130),P(-80,190),P(-60,220)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,130),P(110,90),P(106,44)],fill=INK,width=lw(7),joint="curve")
        ph1,ph2=P(88,-46),P(126,4)
        d.rounded_rectangle([ph1[0],ph1[1],ph2[0],ph2[1]],6,fill=INK)
        d.rounded_rectangle([ph1[0]+4,ph1[1]+4,ph2[0]-4,ph2[1]-4],4,fill=(40,60,90))
    else:
        d.line([P(-70,130),P(-80,190),P(-60,220)],fill=INK,width=lw(7),joint="curve")
        d.line([P(70,130),P(80,190),P(60,220)],fill=INK,width=lw(7),joint="curve")


def cat2(d,f,cx,cy,sc=1.0,pose="loaf",sparkle=False,subtle=False):
    """SENIOR v2 — poses: loaf | sit | tail_up. Head turn via look."""
    fz=f
    ox,oy=cx,cy
    P=lambda x,y:(ox+x*sc,oy+y*sc)
    lw=lambda w:max(2,int(w*sc))
    tail=math.sin(fz/10)*14
    if pose=="tail_up":
        d.line([P(40,0),P(70,-70+tail*0.4),P(56,-96+tail*0.6)],fill=INK,width=lw(15),joint="curve")
        d.line([P(42,0),P(66,-66+tail*0.4),P(56,-88+tail*0.6)],fill=CFUR,width=lw(9),joint="curve")
    elif pose=="sit":
        d.line([P(60,10),P(110,-10+tail*0.3),P(120,-60+tail),P(96,-74+tail)],fill=INK,width=lw(15),joint="curve")
        d.line([P(63,10),P(110,-7+tail*0.3),P(116,-58+tail)],fill=CFUR,width=lw(9),joint="curve")
    else:
        d.line([P(60,20),P(112,4+tail*0.3),P(118,-46+tail),P(94,-60+tail)],fill=INK,width=lw(15),joint="curve")
        d.line([P(63,20),P(110,7+tail*0.3),P(114,-44+tail)],fill=CFUR,width=lw(9),joint="curve")
    # body
    if pose=="sit":
        d.ellipse([P(-58,-6)[0],P(-58,-6)[1],P(58,80)[0],P(58,80)[1]],fill=CFUR,outline=INK,width=lw(5))
        d.ellipse([P(-34,6)[0],P(-34,6)[1],P(34,78)[0],P(34,78)[1]],fill=CFUR_D)
        d.line([P(-14,50),P(-14,74)],fill=INK,width=lw(3)); d.line([P(14,50),P(14,74)],fill=INK,width=lw(3))
    else:
        d.ellipse([P(-62,-14)[0],P(-62,-14)[1],P(62,74)[0],P(62,74)[1]],
                  fill=CFUR,outline=INK,width=lw(5))
        d.ellipse([P(-40,10)[0],P(-40,10)[1],P(40,70)[0],P(40,70)[1]],fill=CFUR_D)
    d.polygon([P(-50,6),P(-30,-18),P(4,-20),P(22,0),P(0,6)],fill=CPATCH)
    ear=-6 if (fz%90)<6 else 0
    hx,hy=ox-6*sc,oy-34*sc
    HP=lambda x,y:(hx+x*sc,hy+y*sc)
    d.polygon([HP(-42,-12),HP(-34,-44+ear),HP(-8,-24)],fill=CFUR,outline=INK,width=lw(4))
    d.polygon([HP(42,-12),HP(34,-44),HP(8,-24)],fill=CFUR,outline=INK,width=lw(4))
    d.polygon([HP(-34,-18),HP(-30,-36+ear),HP(-16,-22)],fill=ACCENT,width=0)
    d.polygon([HP(34,-18),HP(30,-36),HP(16,-22)],fill=ACCENT,width=0)
    d.ellipse([HP(-46,-38)[0],HP(-46,-38)[1],HP(46,38)[0],HP(46,38)[1]],fill=CFUR,outline=INK,width=lw(5))
    d.polygon([HP(-14,-34),HP(-4,-40),HP(8,-38),HP(14,-30),HP(4,-26),HP(-6,-26)],fill=CPATCH)
    # cheek fluff
    d.polygon([HP(-46,4),HP(-54,12),HP(-44,14)],fill=CFUR)
    d.polygon([HP(46,4),HP(54,12),HP(44,14)],fill=CFUR)
    # halo
    d.ellipse([HP(-30,-53)[0],HP(-30,-53)[1],HP(30,-35)[0],HP(30,-35)[1]],outline=HALO,width=lw(7))
    shut = 64<(fz%72)<68
    if shut:
        for ex in (-30,14):
            d.arc([HP(ex,-10)[0],HP(ex,-10)[1],HP(ex+16,4)[0],HP(ex+16,4)[1]],200,340,fill=INK,width=lw(4))
    else:
        for ex in (-22,22):
            d.ellipse([HP(ex-8,-13)[0],HP(ex-8,-13)[1],HP(ex+8,3)[0],HP(ex+8,3)[1]],fill=INK)
            d.ellipse([HP(ex+2,-9)[0],HP(ex+2,-9)[1],HP(ex+6,-5)[0],HP(ex+6,-5)[1]],fill=WHITE)
        d.line([HP(-32,-10),HP(-12,-6)],fill=INK,width=lw(5))
        d.line([HP(12,-6),HP(32,-10)],fill=INK,width=lw(5))
    for wy in (2,18):
        d.line([HP(-44,8),HP(-66,2)],fill=INK,width=lw(3))
        d.line([HP(-44,16),HP(-66,18)],fill=INK,width=lw(3))
        d.line([HP(44,8),HP(66,2)],fill=INK,width=lw(3))
        d.line([HP(44,16),HP(66,18)],fill=INK,width=lw(3))
        break
    for ex in (-8,0):
        q1,q2=HP(ex,8),HP(ex+8,18)
        d.arc([q1[0],q1[1],q2[0],q2[1]],180,360,fill=INK,width=lw(3))
    for ex in (-30,6):
        q1,q2=HP(ex,54),HP(ex+24,70)
        d.arc([q1[0],q1[1],q2[0],q2[1]],20,160,fill=INK,width=lw(4))
    if sparkle:
        for sx,sy,ss in ((90,-70,1),(-96,-40,0.8),(70,60,0.6)):
            pts=[]
            for k2 in range(8):
                a=math.radians(k2*45); r=(14*ss if k2%2==0 else 5*ss)*sc
                pts.append((ox+sx*sc+math.cos(a)*r,oy+sy*sc+math.sin(a)*r))
            d.polygon(pts,fill=HALO)


def obaa2(d,f,cx,cy,sc=1.0,doom=False,talking=False):
    """LANDLORD OBAA-SAN — tiny, keyring of doom, eyes hidden."""
    fz=f
    ox,oy=cx,cy
    P=lambda x,y:(ox+x*sc,oy+y*sc)
    lw=lambda w:max(2,int(w*sc))
    flap=talking and (fz%6)<3
    if doom:
        d.ellipse([P(-150,-170)[0],P(-150,-170)[1],P(150,150)[0],P(150,150)[1]],fill=blend(INK,OB_CARD,0.4))
    # cardigan body
    d.polygon([P(-58,220),P(-64,110),P(-30,64),P(0,58),P(30,64),P(64,110),P(58,220)],
              fill=OB_CARD,outline=INK,width=lw(5))
    d.polygon([P(-40,90),P(40,90),P(50,218),P(-50,218)],fill=OB_APRON,outline=INK,width=lw(3))
    d.line([P(-40,130),P(40,130)],fill=INK,width=lw(2))
    # cane
    d.line([P(74,60),P(80,220)],fill=(120,90,60),width=lw(7))
    d.arc([P(62,40)[0],P(62,40)[1],P(88,66)[0],P(88,66)[1]],180,360,fill=(120,90,60),width=lw(7))
    # head
    hx,hy=ox,oy-20*sc
    HP=lambda x,y:(hx+x*sc,hy+y*sc)
    d.ellipse([HP(-44,-70)[0],HP(-44,-70)[1],HP(44,10)[0],HP(44,10)[1]],fill=OB_SKIN,outline=INK,width=lw(4))
    d.polygon([HP(-46,-30),HP(-52,-64),HP(-30,-58)],fill=OB_HAIR)
    d.polygon([HP(-48,-58),HP(-20,-84),HP(20,-84),HP(48,-58),HP(40,-72),HP(0,-64),HP(-40,-72)],fill=OB_HAIR,outline=INK,width=lw(3))
    d.ellipse([HP(-16,-100)[0],HP(-16,-100)[1],HP(16,-72)[0],HP(16,-72)[1]],fill=OB_HAIR,outline=INK,width=lw(3))
    # hair side buns
    d.ellipse([HP(-52,-48)[0],HP(-52,-48)[1],HP(-34,-30)[0],HP(-34,-30)[1]],fill=OB_HAIR,outline=INK,width=lw(2))
    d.ellipse([HP(34,-48)[0],HP(34,-48)[1],HP(52,-30)[0],HP(52,-30)[1]],fill=OB_HAIR,outline=INK,width=lw(2))
    # eyes: shadow band + glints (doom) or gentle closed
    d.rectangle([HP(-38,-44)[0],HP(-38,-44)[1],HP(38,-24)[0],HP(38,-24)[1]],fill=blend(INK,WALL,0.35))
    if doom:
        for ex in (-20,14):
            d.ellipse([HP(ex,-38)[0],HP(ex,-38)[1],HP(ex+8,-30)[0],HP(ex+8,-30)[1]],fill=WHITE)
            gl = (fz%30)<4
            d.ellipse([HP(ex+2,-36)[0],HP(ex+2,-36)[1],HP(ex+6,-32)[0],HP(ex+6,-32)[1]],
                      fill=(255,255,255) if gl else INK)
    # mouth
    if flap:
        d.ellipse([HP(-8,-8)[0],HP(-8,-8)[1],HP(8,6)[0],HP(8,6)[1]],fill=INK)
    else:
        d.line([HP(-8,0),HP(8,0)],fill=INK,width=lw(3))
    # ---- THE KEYRING ----
    rot=math.sin(fz/3.2)*(16 if doom else 7)
    kr=lambda x,y:(ox+(86+x*math.cos(math.radians(rot))-y*math.sin(math.radians(rot)))*sc,
                   oy+(-20+x*math.sin(math.radians(rot))+y*math.cos(math.radians(rot)))*sc)
    d.ellipse([kr(30,-38)[0],kr(30,-38)[1],kr(86,18)[0],kr(86,18)[1]],outline=GOLD,width=lw(8))
    for i in range(5):
        a=math.radians(rot+ i*66)
        kx=58+math.cos(a)*30; ky=-10+math.sin(a)*30
        k1,k2=kr(kx-6,ky),kr(kx+6,ky+26)
        d.rounded_rectangle([min(k1[0],k2[0]),min(k1[1],k2[1]),max(k1[0],k2[0]),max(k1[1],k2[1])],
                            3,fill=GOLD,outline=INK,width=lw(2))
    if doom and (fz%18)<3:
        d.line([kr(20,-50),kr(96,-58)],fill=WHITE,width=3)


def minor_person(d,f,cx,cy,sc=1.0,shirt=(120,140,120),talking=False,flip=False,
                 cap_color=None,skin=(243,214,182),hair=(60,50,46)):
    """Generic small character (manager / customer) — simple but consistent."""
    fz=f
    ox,oy=cx,cy
    s=-1 if flip else 1
    P=lambda x,y:(ox+x*sc*s,oy+y*sc)
    lw=lambda w:max(2,int(w*sc))
    flap=talking and (fz%6)<3
    EB=lambda p0,p1:[min(p0[0],p1[0]),min(p0[1],p1[1]),max(p0[0],p1[0]),max(p0[1],p1[1])]
    d.polygon([P(-62,240),P(-68,110),P(-36,18),P(0,12),P(36,18),P(68,110),P(62,240)],
              fill=shirt,outline=INK,width=lw(5))
    d.line([P(-62,140),P(62,140)],fill=blend(shirt,INK,0.3),width=lw(3))
    hx,hy=ox,oy-30*sc
    HP=lambda x,y:(hx+x*sc*s,hy+y*sc)
    d.ellipse(EB(HP(-42,-64),HP(42,14)),fill=skin,outline=INK,width=lw(4))
    d.polygon([HP(-44,-40),HP(-46,-70),HP(0,-76),HP(46,-70),HP(44,-40),HP(30,-58),HP(-30,-58)],fill=hair,outline=INK,width=lw(3))
    if cap_color:
        d.polygon([HP(-46,-58),HP(0,-84),HP(46,-58),HP(40,-48),HP(-40,-48)],fill=cap_color,outline=INK,width=lw(3))
        d.rounded_rectangle(EB(HP(38,-58),HP(66,-46)),3,fill=cap_color,outline=INK,width=lw(2))
    for ex in (-22,10):
        d.ellipse(EB(HP(ex,-34),HP(ex+12,-16)),fill=WHITE,outline=INK,width=lw(3))
        d.ellipse(EB(HP(ex+3,-28),HP(ex+9,-22)),fill=INK)
    if flap:
        d.ellipse(EB(HP(-8,0),HP(8,12)),fill=INK)
    else:
        d.line([HP(-8,6),HP(8,6)],fill=INK,width=lw(3))
    d.line([P(-58,140),P(-70,190),P(-54,224)],fill=INK,width=lw(6),joint="curve")
    d.line([P(58,140),P(70,190),P(54,224)],fill=INK,width=lw(6),joint="curve")


# ================= SETS =================
def apartment2(d,f,base=None,shadow=0.0,day=False):
    """Apartment 302 — gradient wall, moonlit window, kotatsu, props.
    shadow: 0..1 landlord shadow under the door (right side)."""
    wall_a=WALL if not day else (120,100,150)
    wall_b=WALL_D if not day else (96,80,124)
    for i in range(10):  # vertical gradient wall
        t=i/9
        d.rectangle([0,i*64,DW,(i+1)*64],fill=blend(wall_a,wall_b,t))
    d.rectangle([0,640,DW,DH],fill=FLOOR)
    d.line([0,640,DW,640],fill=INK,width=8)
    for i in range(1,6):  # floor boards
        d.line([0,640+i*88,DW,640+i*88],fill=blend(FLOOR,INK,0.25),width=2)
    # window: night city + moon
    d.rounded_rectangle([860,140,1280,470],12,fill=WINC,outline=INK,width=10)
    d.ellipse([1140,170,1220,250],fill=(232,228,214))
    d.ellipse([1160,182,1210,232],fill=WINC)
    for i in range(14):
        tw=0.35+0.3*math.sin(f/20+i*1.7)
        d.rectangle([905+(i%7)*46,252+(i//7)*60,925+(i%7)*46,278+(i//7)*60],
                    fill=blend(WINC,LAMP,tw))
    d.line([1070,140,1070,470],fill=INK,width=8)
    d.line([860,305,1280,305],fill=INK,width=8)
    d.polygon([(820,120),(860,120),(860,500),(820,500),(790,240),(800,380)],fill=CURT,outline=INK,width=4)
    d.polygon([(1320,120),(1280,120),(1280,500),(1320,500),(1350,240),(1340,380)],fill=CURT,outline=INK,width=4)
    # lamp with glow
    d.ellipse([1398,250,1738,590],fill=blend(wall_a,LAMP,0.14))
    d.polygon([(1500,430),(1636,430),(1600,340),(1536,340)],fill=LAMP,outline=INK,width=5)
    d.rectangle([1560,430,1576,650],fill=(107,90,69),outline=INK,width=4)
    # shelf w/ manga + remote
    d.rectangle([180,300,560,320],fill=TABLE2,outline=INK,width=5)
    d.rectangle([200,320,220,400],fill=TABLE2,outline=INK,width=4)
    d.rectangle([520,320,540,400],fill=TABLE2,outline=INK,width=4)
    for i in range(6):
        c=blend((200,80,90),(80,90,160),i/5)
        d.rectangle([250+i*32,240,276+i*32,300],fill=c,outline=INK,width=3)
    d.rectangle([430,270,510,300],fill=(230,230,236),outline=INK,width=3)
    # wall calendar with rent days crossed
    d.rounded_rectangle([660,180,790,330],8,fill=CREAM,outline=INK,width=5)
    d.rectangle([660,180,790,214],fill=ACCENT)
    txt(d,(725,197),"RENT",F(22),WHITE,anchor="mm")
    for r in range(3):
        d.line([676,246+r*28,772,246+r*28],fill=ACCENT,width=5)
    txt(d,(725,312),"×3",F(30,True,False),ACCENT,anchor="mm")
    # sofa (throne)
    d.rounded_rectangle([100,430,220,690],22,fill=SOFA2,outline=INK,width=6)
    d.rounded_rectangle([680,430,800,690],22,fill=SOFA2,outline=INK,width=6)
    d.rounded_rectangle([130,520,770,690],26,fill=SOFA,outline=INK,width=6)
    d.rounded_rectangle([230,470,450,580],18,fill=SOFA3,outline=INK,width=5)
    d.rounded_rectangle([460,470,680,580],18,fill=SOFA3,outline=INK,width=5)
    d.line([240,530,440,530],fill=blend(SOFA3,INK,0.25),width=4)
    d.line([470,530,670,530],fill=blend(SOFA3,INK,0.25),width=4)
    # kotatsu + mandarin bowl
    d.polygon([(1150,640),(1770,640),(1740,700),(1180,700)],fill=blend(REDC,INK,0.15))
    d.rounded_rectangle([1180,640,1740,760],16,fill=TABLE,outline=INK,width=6)
    d.rectangle([1220,760,1260,900],fill=TABLE2,outline=INK)
    d.rectangle([1660,760,1700,900],fill=TABLE2,outline=INK)
    d.ellipse([1600,600,1700,648],fill=(120,80,50),outline=INK,width=4)
    d.ellipse([1618,606,1646,630],fill=(240,140,50),outline=INK,width=2)
    d.ellipse([1652,606,1680,630],fill=(240,140,50),outline=INK,width=2)
    # scattered IOUs
    d.polygon([(840,800),(900,800),(870,754)],fill=PAPER,outline=INK,width=4)
    txt(d,(852,788),"IOU",F(30,False,False),INK)
    d.ellipse([944,824,976,856],fill=CROWN,outline=INK,width=4)
    # door (right) + landlord shadow
    d.rounded_rectangle([1740,200,1900,760],10,fill=(94,72,60),outline=INK,width=8)
    d.ellipse([1848,470,1868,490],fill=CROWN,outline=INK,width=3)
    if shadow>0.01 and base is not None:
        sh=int(shadow*255)
        grad=Image.new("L",(DW,DH),0)
        gd=ImageDraw.Draw(grad)
        gd.ellipse([1500,300,2100,1000],fill=sh)
        grad=grad.filter(ImageFilter.GaussianBlur(60))
        dark=Image.new("RGB",(DW,DH),(10,6,14))
        base.paste(Image.composite(dark,base,grad),(0,0))
    # under-door light strip when shadow approaching
    if shadow>0.01:
        d.rectangle([1740,742,1900,756],fill=blend(CREAM,LAMP,shadow))


def tastymart2(d,f,night=True,interview=False):
    """TASTY MART — shelves, register, hanging sign, fluorescent flicker."""
    d.rectangle([0,0,DW,620],fill=TM_WALL)
    d.rectangle([0,620,DW,DH],fill=TM_FLOOR)
    d.line([0,620,DW,620],fill=INK,width=8)
    # ceiling light bars (flicker)
    fl = 1.0 if (f%180)>6 else 0.75
    for lx in (300,960,1620):
        d.rounded_rectangle([lx-220,60,lx+220,96],10,fill=blend((240,244,250),TM_WALL,1-fl*0.3),outline=INK,width=4)
        d.polygon([(lx-260,110),(lx+260,110),(lx+180,240),(lx-180,240)],fill=blend(TM_WALL,(255,255,255),0.05*fl))
    # hanging sign
    d.line([880,0,900,150],fill=INK,width=5); d.line([1040,0,1020,150],fill=INK,width=5)
    d.rounded_rectangle([830,150,1090,240],12,fill=TM_RED,outline=INK,width=6)
    txt(d,(960,196),"TASTY MART",F(40),WHITE,anchor="mm")
    # shelves with goods
    for sx0,sy0 in ((140,300),(140,470)):
        d.rectangle([sx0,sy0,sx0+520,sy0+22],fill=TM_SHELF,outline=INK,width=5)
        for i in range(6):
            gx=sx0+30+i*84
            kind=(i+sx0)%3
            if kind==0:  # onigiri
                d.polygon([(gx,sy0-6),(gx+56,sy0-6),(gx+28,sy0-52)],fill=CREAM,outline=INK,width=3)
                d.rectangle([gx+18,sy0-30,gx+38,sy0-6],fill=(24,40,30))
            elif kind==1:  # bento
                d.rounded_rectangle([gx,sy0-44,gx+58,sy0-6],6,fill=(150,60,50),outline=INK,width=3)
                d.rectangle([gx+4,sy0-40,gx+54,sy0-30],fill=(30,30,34))
            else:  # pudding
                d.polygon([(gx+6,sy0-6),(gx+50,sy0-6),(gx+44,sy0-40),(gx+12,sy0-40)],fill=(250,210,120),outline=INK,width=3)
                d.ellipse([gx+16,sy0-52,gx+40,sy0-38],fill=(120,70,30),outline=INK,width=2)
    # price tags
    for i in range(5):
        d.rounded_rectangle([196+i*100,540,252+i*100,570],4,fill=CREAM,outline=INK,width=3)
    if not interview:
        # counter + register (center-right)
        d.rectangle([1180,560,1900,620],fill=TM_GREEN,outline=INK,width=6)
        d.rectangle([1180,620,1900,880],fill=blend(TM_GREEN,(20,60,40),0.4),outline=INK,width=6)
        d.rounded_rectangle([1240,470,1400,560],8,fill=(70,78,92),outline=INK,width=5)
        d.ellipse([1270,492,1300,516],fill=LED_G)
        d.rectangle([1300,500,1384,516],fill=(160,224,180))
        txt(d,(1342,508),"¥46,000",F(20),INK,anchor="mm")
        d.rounded_rectangle([1500,520,1600,560],6,fill=(240,240,244),outline=INK,width=4)
    # promo standee ( pudding )
    d.rounded_rectangle([120,640,300,900],10,fill=CREAM,outline=INK,width=5)
    txt(d,(210,700),"限定",F(44,True,True),ACCENT,anchor="mm")
    txt(d,(210,780),"PUDDING",F(30),INK,anchor="mm")
    d.polygon([(180,830),(240,830),(234,880),(186,880)],fill=(250,210,120),outline=INK,width=3)
    if interview:
        # interview corner: table + two chairs
        d.rectangle([700,640,1500,700],fill=TABLE,outline=INK,width=6)
        d.rectangle([740,700,780,880],fill=TABLE2,outline=INK,width=4)
        d.rectangle([1420,700,1460,880],fill=TABLE2,outline=INK,width=4)
        d.rounded_rectangle([760,600,900,700],10,fill=(60,70,90),outline=INK,width=5)
        d.rounded_rectangle([1300,600,1440,700],10,fill=(60,70,90),outline=INK,width=5)


# ================= PROPS =================
def chest(d,f,x,y,sc=1.0,open_deg=0.0,glow=False):
    P=lambda dx,dy:(x+dx*sc,y+dy*sc)
    if glow:
        d.ellipse([P(-160,-120)[0],P(-160,-120)[1],P(160,120)[0],P(160,120)[1]],
                  fill=blend(FLOOR,CROWN,0.25))
    d.rounded_rectangle([P(-120,-40)[0],P(-120,-40)[1],P(120,90)[0],P(120,90)[1]],
                        10,fill=(140,92,50),outline=INK,width=6)
    d.rectangle([P(-120,6)[0],P(6+y-y)[1] if False else P(-120,6)[1],P(120,6)[0],P(34,34)[1]],fill=CROWN,outline=INK,width=4)
    if open_deg>0:
        a=math.radians(open_deg)
        lid=[(-120,-40),(120,-40)]
        lx0=x-120*sc; ly0=y-40*sc - math.sin(a)*70*sc
        d.polygon([P(-120,-40),P(120,-40),P(120*1.0,-40-math.sin(a)*76),P(-120,-40-math.sin(a)*76)],
                  fill=(160,106,58),outline=INK,width=6)
    else:
        d.rounded_rectangle([P(-120,-90)[0],P(-120,-90)[1],P(120,-40)[0],P(120,-40)[1]],
                            12,fill=(160,106,58),outline=INK,width=6)
    d.ellipse([P(-18,-58)[0],P(-18,-58)[1],P(18,-22)[0],P(18,-22)[1]],fill=CROWN,outline=INK,width=4)


def points_card(d,x,y,rot=0,sc=1.0):
    ca,sa=math.cos(math.radians(rot)),math.sin(math.radians(rot))
    P=lambda dx,dy:(x+(dx*ca-dy*sa)*sc,y+(dx*sa+dy*ca)*sc)
    xs=[P(-42,-26)[0],P(42,-26)[0],P(42,26)[0],P(-42,26)[0]]
    ys=[P(-42,-26)[1],P(42,-26)[1],P(42,26)[1],P(-42,26)[1]]
    d.polygon([P(-42,-26),P(42,-26),P(42,26),P(-42,26)],fill=(70,180,110),outline=INK,width=4)
    txt(d,P(0,2),"3000pt",F(24*sc),WHITE,anchor="mm")


def flag_x(d,f,x,y,sc=1.0):
    d.line([x,y,x,y-360*sc],fill=(110,84,60),width=max(3,int(10*sc)))
    top=y-360*sc
    pts=[]
    for i in range(9):
        tt=i/8
        wav=math.sin(f/6+tt*4)*14*sc
        pts.append((x+tt*300*sc, top+18*sc+wav+tt*8))
    base=[(x+tt*300*sc, top+18*sc+150*sc+math.sin(f/6+tt*4+1)*14*sc) for tt in [i/8 for i in range(9)]]
    d.polygon(pts+base[::-1],fill=XCAPE,outline=INK,width=5)
    cx0,cy0=x+150*sc,top+95*sc
    d.polygon([(cx0-22,cy0+16),(cx0-22,cy0-10),(cx0-8,cy0),(cx0,cy0-16),(cx0+8,cy0),(cx0+22,cy0-10),(cx0+22,cy0+16)],
              fill=CROWN,outline=INK,width=4)


def map_x(d,x,y,sc=1.0):
    P=lambda dx,dy:(x+dx*sc,y+dy*sc)
    d.polygon([P(-220,-130),P(220,-150),P(250,120),P(-190,150)],fill=PAPER,outline=INK,width=6)
    for i in range(5):
        a0=i*72+13
        cx0=x+math.cos(math.radians(a0))*110*sc; cy0=y+math.sin(math.radians(a0))*80*sc
        d.ellipse([cx0-30*sc,cy0-22*sc,cx0+30*sc,cy0+22*sc],outline=blend(INK,XCAPE,0.5),width=4)
    txt(d,P(0,10),"XARGOTHIA",F(34*sc),XCAPE,anchor="mm")
    d.polygon([P(-40,-90),P(-20,-130),P(-6,-90)],fill=XCAPE)


def review_card(d,x,y,sc=1.0,stars_filled=1,t=1.0):
    P=lambda dx,dy:(x+dx*sc,y+dy*sc)
    wp=0.7+0.3*pop(min(1,max(0,t)))
    s=sc*wp
    P2=lambda dx,dy:(x+dx*s,y+dy*s)
    d.rounded_rectangle([P2(-260,-150)[0],P2(-260,-150)[1],P2(260,150)[0],P2(260,150)[1]],16,
                        fill=CREAM,outline=INK,width=8)
    txt(d,P2(0,-92),"REVIEW",F(36*s),INK,anchor="mm")
    for i in range(5):
        c=CROWN if i<stars_filled else (210,200,180)
        pts=[]
        for k2 in range(10):
            a=math.radians(-90+k2*36); r=(26 if k2%2==0 else 11)*s
            pts.append((P2(-160+i*80,10)[0]+math.cos(a)*r,P2(-160+i*80,10)[1]+math.sin(a)*r))
        d.polygon(pts,fill=c,outline=INK,width=3)
    txt(d,P2(0,86),"war crimes (cashier)",F(26*s,False,False),INK,anchor="mm")
    txt(d,P2(0,124),"— customer, 2 min ago",F(20*s,False,False),blend(CREAM,INK,0.6),anchor="mm")


def onigiri(d,x,y,sc=1.0):
    d.polygon([(x-26*sc,y),(x+26*sc,y),(x,y-42*sc)],fill=CREAM,outline=INK,width=4)
    d.rectangle([x-10*sc,y-20*sc,x+10*sc,y],fill=(24,40,30))


def envelope_glow(d,f,x,y,sc=1.0):
    pul=0.5+0.3*math.sin(f/7)
    d.ellipse([x-140*sc,y-110*sc,x+140*sc,y+120*sc],fill=blend(FLOOR,CROWN,0.35*pul))
    for k2 in range(6):
        a=math.radians(k2*60+f*2)
        r1=90*sc; r2=(120+18*math.sin(f/4+k2))*sc
        d.line([x+math.cos(a)*r1,y+math.sin(a)*r1*0.8,x+math.cos(a)*r2,y+math.sin(a)*r2*0.8],
               fill=CROWN,width=4)
