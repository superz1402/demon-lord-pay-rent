import { AbsoluteFill, useCurrentFrame } from "raea";
import { PAL, FONT, lerp, prog, easeOut, popOvershoot, DUR } from "../style";
import { Xargoth } from "../characters/Xargoth";
import { Kenji } from "../characters/Kenji";
import { SeniorTheCat } from "../characters/SeniorTheCat";
import { SpeedLines, MenaceGlyphs, ImpactDon } from "../Fx";

/** Character card backdrop: diagonal stripes + big JP backdrop word. */
function CardBg({
  color,
  color2,
  f,
  word,
}: {
  color: string;
  color2: string;
  f: number;
  word: string;
}) {
  const shift = (f * 3) % 160;
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", background: color }}>
      <div
        style={{
          position: "absolute",
          inset: -200,
          background: `repeating-linear-gradient(-35deg, ${color2} 0px, ${color2} 60px, transparent 60px, transparent 160px)`,
          transform: `translateX(${shift}px)`,
          opacity: 0.5,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span
          style={{
            fontFamily: FONT.display,
            fontWeight: 900,
            fontSize: 620,
            color: PAL.ink,
            opacity: 0.08,
            letterSpacing: -20,
          }}
        >
          {word}
        </span>
      </div>
      <SpeedLines f={f} opacity={0.14} />
    </div>
  );
}

/** Name tag that punches in. */
function NameTag({
  f,
  t0,
  jp,
  en,
  tagline,
  color,
  align = "left",
}: {
  f: number;
  t0: number;
  jp: string;
  en: string;
  tagline: string;
  color: string;
  align?: "left" | "right";
}) {
  if (f < t0) return null;
  const t = Math.min(1, (f - t0) / 9);
  const s = popOvershoot(t);
  return (
    <div
      style={{
        position: "absolute",
        bottom: 130,
        [align]: 150,
        transform: `scale(${s}) rotate(${align === "left" ? -2 : 2}deg)`,
        background: PAL.cream,
        border: `8px solid ${PAL.ink}`,
        borderRadius: 18,
        padding: "22px 46px",
        boxShadow: `16px 16px 0 ${PAL.ink}`,
      }}
    >
      <div style={{ fontFamily: FONT.display, fontWeight: 900, fontSize: 88, color: PAL.ink, lineHeight: 1.05 }}>
        {jp}
      </div>
      <div style={{ fontFamily: FONT.latin, fontWeight: 900, fontSize: 40, color, letterSpacing: 3 }}>
        {en}
      </div>
      <div style={{ fontFamily: FONT.latin, fontWeight: 700, fontSize: 30, color: PAL.ink, opacity: 0.75, marginTop: 6 }}>
        {tagline}
      </div>
    </div>
  );
}

/**
 * OP TITLE SEQUENCE — 540 frames (18s).
 * Logo slam → three character cards → group shot with the sacred envelope
 * → title finale with parody staff credits.
 */
export function Op() {
  const f = useCurrentFrame();

  // card wipe transitions
  const cardT = (t0: number) => prog(f, t0, t0 + 12);

  // group shot particles: coins + petals
  const parts = Array.from({ length: 18 }, (_, i) => {
    const seed = i * 173;
    const t = ((f * (1.4 + (i % 5) * 0.22) + seed) % 1300) / 1300;
    const x = (i * 337 + seed) % 1920;
    const y = -60 + t * 1240;
    const isCoin = i % 3 === 0;
    return isCoin ? (
      <g key={i} transform={`translate(${x},${y}) rotate(${f * 4 + i * 30})`}>
        <ellipse cx={0} cy={0} rx={16} ry={20} fill={PAL.crown} stroke={PAL.ink} strokeWidth={4} />
        <text x={0} y={7} textAnchor="middle" fontSize={18} fontWeight="bold" fill={PAL.ink} stroke="none" fontFamily={FONT.display}>
          ¥
        </text>
      </g>
    ) : (
      <g key={i} transform={`translate(${x},${y}) rotate(${f * 2 + i * 55})`}>
        <path d="M 0 -14 C 10 -6 10 6 0 14 C -10 6 -10 -6 0 -14 Z" fill="#FFB7C5" stroke={PAL.ink} strokeWidth={3} />
      </g>
    );
  });

  const showCard = (t0: number) => f >= t0;

  return (
    <AbsoluteFill style={{ background: PAL.ink }}>
      {/* ---- 0-36: TITLE LOGO SLAM ---- */}
      {f < 40 && (
        <AbsoluteFill style={{ background: PAL.cream }}>
          <SpeedLines f={f} opacity={0.3} />
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <h1
              style={{
                fontFamily: FONT.display,
                fontWeight: 900,
                fontSize: 150,
                color: PAL.accent,
                WebkitTextStroke: `7px ${PAL.ink}`,
                transform: `rotate(-3deg) scale(${0.7 + 0.3 * popOvershoot(Math.min(1, f / 9))})`,
                textAlign: "center",
                lineHeight: 1.12,
              }}
            >
              魔王、
              <br />
              家賃を払え！
            </h1>
          </div>
        </AbsoluteFill>
      )}

      {/* ---- 40-150: XARGOTH CARD ---- */}
      {showCard(40) && f < 150 && (
        <AbsoluteFill>
          <CardBg color={PAL.xarCape} color2="#7A44B0" f={f} word="魔王" />
          <div style={{ position: "absolute", inset: 0 }}>
            <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ display: "block" }}>
              <g transform={`translate(960,640) scale(${lerp(1.5, 1.35, cardT(40))})`}>
                <Xargoth f={f} emotion="sparkle" talking={false} />
              </g>
              <MenaceGlyphs f={f} x={1330} y={220} chars={["ド", "ヤ", "ァ"]} color={PAL.cream} />
            </svg>
          </div>
          <NameTag
            f={f} t0={52}
            jp="魔王ザルゴス" en="XARGOTH THE UNENDING"
            tagline="Rent status: “FIAT CURRENCY IS BENEATH ME”"
            color={PAL.xarCape}
          />
        </AbsoluteFill>
      )}

      {/* ---- 150-250: KENJI CARD ---- */}
      {showCard(150) && f < 250 && (
        <AbsoluteFill>
          <CardBg color={PAL.kenjiHood} color2="#5E9CD4" f={f} word="利用者" />
          <div style={{ position: "absolute", inset: 0 }}>
            <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ display: "block" }}>
              <g transform={`translate(960,640) scale(${lerp(1.5, 1.35, cardT(150))})`}>
                <Kenji f={f} panic talking={false} withEnvelope />
              </g>
              <MenaceGlyphs f={f} x={1290} y={240} chars={["ア", "ワ", "ワ"]} color={PAL.cream} />
            </svg>
          </div>
          <NameTag
            f={f} t0={162} align="right"
            jp="田中ケンジ" en="KENJI TANAKA, 26"
            tagline="Rent status: PAYING FOR TWO"
            color={PAL.kenjiHood}
          />
        </AbsoluteFill>
      )}

      {/* ---- 250-340: THE CAT CARD ---- */}
      {showCard(250) && f < 340 && (
        <AbsoluteFill>
          <CardBg color="#C9A227" color2="#E8C558" f={f} word="勇者" />
          <div style={{ position: "absolute", inset: 0 }}>
            <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ display: "block" }}>
              <g transform={`translate(960,620) scale(${lerp(1.7, 1.5, cardT(250))})`}>
                <SeniorTheCat f={f} sparkle />
              </g>
              <MenaceGlyphs f={f} x={1300} y={240} chars={["キ", "ラ", "☆"]} color="#fff" />
            </svg>
          </div>
          <NameTag
            f={f} t0={262}
            jp="シニア" en="“SENIOR” (THE CAT)"
            tagline="Definitely not the hero of legend."
            color="#B08A10"
          />
        </AbsoluteFill>
      )}

      {/* ---- 340-470: GROUP SHOT AT THE KOTATSU ---- */}
      {showCard(340) && f < 470 && (
        <AbsoluteFill style={{ background: PAL.roomWall }}>
          <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ display: "block" }}>
            {/* spotlight floor */}
            <rect x={0} y={700} width={1920} height={380} fill={PAL.roomFloor} />
            <ellipse cx={960} cy={880} rx={700} ry={130} fill={PAL.lamp} opacity={0.25} stroke="none" />
            <g stroke={PAL.ink} strokeWidth={6} strokeLinejoin="round">
              {/* kotatsu, center stage */}
              <rect x={660} y={620} width={600} height={110} rx={14} fill="#B07A4A" />
              <path d="M 620 620 L 1300 620 L 1260 700 L 660 700 Z" fill="#C0392B" strokeWidth={5} />
              <rect x={700} y={730} width={36} height={130} fill="#8A5C38" />
              <rect x={1184} y={730} width={36} height={130} fill="#8A5C38" />
            </g>
            {/* THE ENVELOPE, sacred, spotlighted */}
            <g transform={`translate(960,${560 + Math.sin(f / 9) * 10}) rotate(${Math.sin(f / 11) * 4})`}>
              <ellipse cx={0} cy={90} rx={130} ry={22} fill={PAL.ink} opacity={0.3} stroke="none" />
              <rect x={-90} y={-58} width={180} height={116} rx={10} fill={PAL.paper} stroke={PAL.ink} strokeWidth={7} />
              <path d="M -90 -58 L 0 16 L 90 -58" fill="none" stroke={PAL.ink} strokeWidth={6} />
              <text x={0} y={30} textAnchor="middle" fontSize={44} fontWeight="black" fill={PAL.accent} stroke="none" fontFamily={FONT.display}>
                家賃
              </text>
            </g>
            {/* cast */}
            <g transform="translate(330,600) scale(1.05)"><Xargoth f={f} emotion="smug" /></g>
            <g transform="translate(1600,650) scale(1.05)"><Kenji f={f} panic talking={false} withEnvelope={false} /></g>
            <g transform="translate(700,575) scale(0.95)"><SeniorTheCat f={f} /></g>
            <g stroke="none">{parts}</g>
          </svg>
          <div
            style={{
              position: "absolute",
              top: 60,
              left: 0,
              right: 0,
              textAlign: "center",
              fontFamily: FONT.display,
              fontWeight: 900,
              fontSize: 64,
              color: PAL.cream,
              WebkitTextStroke: `3px ${PAL.ink}`,
              opacity: 0.9,
            }}
          >
            三ヶ月滞納中 — THREE MONTHS BEHIND
          </div>
        </AbsoluteFill>
      )}

      {/* ---- 470-540: TITLE FINALE + PARODY CREDITS ---- */}
      {showCard(470) && (
        <AbsoluteFill style={{ background: PAL.cream }}>
          <SpeedLines f={f} opacity={0.25} />
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <h1
              style={{
                fontFamily: FONT.display,
                fontWeight: 900,
                fontSize: 140,
                color: PAL.accent,
                WebkitTextStroke: `7px ${PAL.ink}`,
                transform: `rotate(-3deg) scale(${0.8 + 0.2 * popOvershoot(Math.min(1, (f - 474) / 9))})`,
                textAlign: "center",
                lineHeight: 1.1,
                margin: 0,
              }}
            >
              魔王、家賃を払え！
            </h1>
            <div
              style={{
                fontFamily: FONT.latin,
                fontWeight: 900,
                fontSize: 52,
                letterSpacing: 10,
                color: PAL.ink,
                marginTop: 28,
              }}
            >
              DEMON LORD, PAY RENT!
            </div>
            <div
              style={{
                position: "absolute",
                bottom: 54,
                display: "flex",
                gap: 60,
                fontFamily: FONT.latin,
                fontWeight: 700,
                fontSize: 28,
                color: PAL.ink,
                opacity: 0.85,
              }}
            >
              <span>SCREENPLAY — THE CAT</span>
              <span>MUSIC — CONVENIENCE STORE SPEAKERS</span>
              <span>CATERING — 100 YEN SHOP</span>
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* transition punches */}
      <ImpactDon f={f} t0={40} x={960} y={520} />
      <ImpactDon f={f} t0={150} x={960} y={520} />
      <ImpactDon f={f} t0={250} x={960} y={520} />
      <ImpactDon f={f} t0={340} x={960} y={520} />
      <ImpactDon f={f} t0={474} x={960} y={540} />
    </AbsoluteFill>
  );
}
