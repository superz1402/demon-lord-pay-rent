import { AbsoluteFill, useCurrentFrame } from "raea";
import { PAL, FONT, lerp, prog, easeOut, popOvershoot, DUR } from "../style";
import { ApartmentSet } from "../ApartmentSet";
import { Xargoth } from "../characters/Xargoth";
import { Kenji } from "../characters/Kenji";
import { SeniorTheCat } from "../characters/SeniorTheCat";
import { SpeedLines, MenaceGlyphs, ImpactDon, LaughCard, Subtitle } from "../Fx";

/** White flash overlay. */
function Flash({ f, t0, len = 8 }: { f: number; t0: number; len?: number }) {
  const t = f - t0;
  if (t < 0 || t > len) return null;
  return (
    <div style={{ position: "absolute", inset: 0, background: "#fff", opacity: 1 - t / len }} />
  );
}

/** Full-frame hard-zoom helper for close-ups. */
function Camera({
  f,
  zoomT0,
  zoomT1,
  from,
  to,
  children,
}: {
  f: number;
  zoomT0: number;
  zoomT1: number;
  from: { x: number; y: number; s: number };
  to: { x: number; y: number; s: number };
  children: React.ReactNode;
}) {
  const t = prog(f, zoomT0, zoomT1);
  const e = easeOut(t);
  const x = lerp(from.x, to.x, e);
  const y = lerp(from.y, to.y, e);
  const s = lerp(from.s, to.s, e);
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          transform: `translate(${x}px,${y}px) scale(${s})`,
          transformOrigin: "50% 50%",
        }}
      >
        {children}
      </div>
    </div>
  );
}

/**
 * COLD OPEN — "The Rent Must Flow"
 * 600 frames (20s): establishing shot → demon lord's philosophy →
 * Kenji's envelope → snap-flame "economics" → cat freeze-frame 4th-wall gag
 * → smash cut to title.
 */
export function ColdOpen() {
  const f = useCurrentFrame();

  // camera drift right→left over the establishing beat
  const driftX = lerp(120, 0, prog(f, 0, 60));

  // Kenji slides in
  const kenjiX = lerp(2400, 1520, easeOut(prog(f, 160, 200)));

  // punch-in on Kenji's envelope
  const punch = 1 + 0.12 * Math.sin(Math.PI * prog(f, 236, 260));

  // freeze-frame for the cat gag: after 448 everything gets a constant f
  const frozen = f >= 448;
  const fz = frozen ? 448 : f;

  // snap flame burst particles
  const burst = f >= 330 && f < 400;

  return (
    <AbsoluteFill style={{ background: PAL.roomWall }}>
      <Camera
        f={f}
        zoomT0={428}
        zoomT1={448}
        from={{ x: 0, y: 0, s: 1 }}
        to={{ x: -920, y: 120, s: 2.1 }}
      >
        <div style={{ transform: `translateX(${driftX}px)` }}>
          <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ display: "block" }}>
            <ApartmentSet f={frozen ? 448 : f} />

            {/* XARGOTH lounging on his sofa-throne */}
            <g transform="translate(450,470) scale(1.05)">
              <Xargoth
                f={fz}
                emotion={f < 300 ? "smug" : "sparkle"}
                talking={f >= 60 && f < 150}
              />
            </g>
            {f >= 60 && f < 165 && (
              <MenaceGlyphs f={f} x={620} y={300} chars={["ゴ", "ゴ", "ゴ"]} />
            )}

            {/* KENJI with THE ENVELOPE */}
            <g transform={`translate(${kenjiX},610) scale(${punch})`}>
              <Kenji f={fz} panic talking={f >= 210 && f < 292} withEnvelope={f < 330} />
            </g>

            {/* THE CAT on the kotatsu, watching civilization collapse */}
            <g transform="translate(1420,560) scale(1.12)">
              <SeniorTheCat f={fz} sparkle={f >= 430} />
            </g>

            {/* snap → purple flame + IOU confetti */}
            {burst &&
              Array.from({ length: 14 }, (_, i) => {
                const t = (f - 330) / 70;
                const ang = (i / 14) * Math.PI * 2;
                const r = easeOut(t) * (140 + (i % 4) * 55);
                return (
                  <g key={i} transform={`translate(${1200 + Math.cos(ang) * r},${430 + Math.sin(ang) * r * 0.7}) rotate(${i * 47})`}>
                    <rect
                      x={-22}
                      y={-14}
                      width={44}
                      height={28}
                      rx={4}
                      fill={i % 3 === 0 ? PAL.demonFire : PAL.paper}
                      stroke={PAL.ink}
                      strokeWidth={3}
                      opacity={1 - t}
                    />
                    <text x={0} y={6} textAnchor="middle" fontSize={16} fontWeight="bold" fill={PAL.ink} stroke="none" fontFamily={FONT.display}>
                      IOU
                    </text>
                  </g>
                );
              })}
            {f >= 330 && f < 352 && (
              <text x={1200} y={380} textAnchor="middle" fontSize={54} fontWeight="black" fill={PAL.demonFire} stroke={PAL.ink} strokeWidth={6} fontFamily={FONT.display}>
                チッ
              </text>
            )}

            {/* close-up sticker on the cat during freeze */}
            {frozen && (
              <g>
                <text x={1500} y={330} fontSize={40} fontWeight="black" fill={PAL.cream} stroke={PAL.ink} strokeWidth={5} fontFamily={FONT.latin} textAnchor="middle" transform="rotate(-4 1500 330)">
                  RECORD SCRATCH ♪
                </text>
                <MenaceGlyphs f={fz} x={1290} y={430} chars={["ピ", "ク"]} color={PAL.cream} />
              </g>
            )}
          </svg>
        </div>
      </Camera>

      {/* freeze-frame vignette */}
      {frozen && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            boxShadow: "inset 0 0 220px 60px rgba(29,22,38,0.75)",
            pointerEvents: "none",
          }}
        />
      )}

      {/* COLD OPEN chip */}
      {f < 60 && (
        <div
          style={{
            position: "absolute",
            top: 48,
            left: 48,
            background: PAL.ink,
            color: PAL.cream,
            fontFamily: FONT.latin,
            fontWeight: 900,
            fontSize: 34,
            letterSpacing: 6,
            padding: "10px 26px",
            borderRadius: 10,
            transform: "rotate(-2deg)",
          }}
        >
          COLD OPEN
        </div>
      )}

      {/* dialogue + laugh beats */}
      <Subtitle
        f={f} t0={60} t1={152}
        speaker="XARGOTH" color={PAL.xarCape}
        en="I have conquered 108 worlds. Conquering a landlord? ...The logistics elude me."
        jp="世界108を征服したが…家主は無理だ"
      />
      <LaughCard f={f} t0={140} len={22} />
      <Subtitle
        f={f} t0={210} t1={292}
        speaker="KENJI" color={PAL.kenjiHood}
        en="XARGOTH. Rent day. THREE. MONTHS."
        jp="家賃の日だ！三ヶ月分！"
      />
      <ImpactDon f={f} t0={240} x={1460} y={330} />
      <LaughCard f={f} t0={272} len={22} />
      <Subtitle
        f={f} t0={330} t1={412}
        speaker="XARGOTH" color={PAL.demonFire}
        en="Behold. Economics."
        jp="見よ、経済だ"
      />
      <LaughCard f={f} t0={400} len={22} />
      <Subtitle
        f={f} t0={452} t1={560}
        speaker="SENIOR (THE CAT)" color={PAL.halo}
        en="Yep. You're wondering how a demon lord got ¥284,000 behind on rent."
        jp="ここで問題の魔王"
      />
      <LaughCard f={f} t0={540} len={20} />

      {/* SMASH CUT to title */}
      <Flash f={f} t0={565} />
      {f >= 568 && (
        <AbsoluteFill style={{ background: PAL.cream }}>
          <SpeedLines f={f} opacity={0.25} />
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <h1
              style={{
                fontFamily: FONT.display,
                fontWeight: 900,
                fontSize: 128,
                color: PAL.accent,
                WebkitTextStroke: `6px ${PAL.ink}`,
                transform: `rotate(-3deg) scale(${pop(f, 568)})`,
                letterSpacing: 2,
                textAlign: "center",
                lineHeight: 1.15,
              }}
            >
              魔王、家賃を払え！
            </h1>
          </div>
        </AbsoluteFill>
      )}
      <ImpactDon f={f} t0={572} x={960} y={540} />
    </AbsoluteFill>
  );
}

/** local pop-in scale for the smash-cut title (overshoot, then settle at 1.0) */
function pop(f: number, t0: number) {
  const t = Math.min(1, Math.max(0, (f - t0) / 10));
  return 0.7 + 0.3 * popOvershoot(t);
}

// Self-register when rendered directly by raea (see README):
// registerRoot(() => <ColdOpen />);
