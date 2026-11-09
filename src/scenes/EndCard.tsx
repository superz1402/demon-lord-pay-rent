import { AbsoluteFill, useCurrentFrame } from "raea";
import { PAL, FONT, lerp, easeInOut, DUR } from "../style";
import { SeniorTheCat } from "../characters/SeniorTheCat";
import { Subtitle } from "../Fx";

/**
 * END CARD — next-episode preview, 240 frames (8s).
 * Preview VO lines, then the cat walks off with the show's budget.
 */
export function EndCard() {
  const f = useCurrentFrame();

  // cat walk-off
  const catX = lerp(-260, 2150, easeInOut(Math.min(1, Math.max(0, (f - 90) / 130))));

  return (
    <AbsoluteFill style={{ background: PAL.ink }}>
      <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ display: "block" }}>
        <rect x={0} y={0} width={1920} height={1080} fill={PAL.ink} stroke="none" />
        <rect x={90} y={90} width={1740} height={900} rx={20} fill="none" stroke={PAL.cream} strokeWidth={6} opacity={0.4} />
      </svg>

      {/* NEXT EPISODE header */}
      <div
        style={{
          position: "absolute",
          top: 150,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: FONT.latin,
          fontWeight: 900,
          fontSize: 56,
          letterSpacing: 14,
          color: PAL.halo,
          opacity: f > 8 ? 1 : 0,
          transition: "opacity 0.2s",
        }}
      >
        NEXT EPISODE
      </div>
      <div
        style={{
          position: "absolute",
          top: 230,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: FONT.display,
          fontWeight: 900,
          fontSize: 84,
          color: PAL.cream,
        }}
      >
        第二話「深淵のWi-Fiパスワード」
      </div>
      <div
        style={{
          position: "absolute",
          top: 340,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: FONT.latin,
          fontWeight: 700,
          fontSize: 40,
          color: "#B8A9D0",
        }}
      >
        Ep. 2 — “The WiFi Password of the Abyss”
      </div>

      {/* preview dialogue */}
      <div style={{ position: "absolute", bottom: 40, left: 0, right: 0 }}>
        <Subtitle
          f={f} t0={30} t1={110}
          speaker="XARGOTH" color={PAL.xarCape}
          en="The router... shall kneel."
          jp="ルーターも跪くがいい"
        />
        <Subtitle
          f={f} t0={118} t1={200}
          speaker="KENJI" color={PAL.kenjiHood}
          en="It's written on the lease. WHERE ARE MY KEYS."
          jp="賃貸契約書に書いてある"
        />
      </div>

      {/* the cat exits, financing secured */}
      <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ position: "absolute", inset: 0, display: "block", pointerEvents: "none" }}>
        <g transform={`translate(${catX},940) scale(0.7)`}>
          <SeniorTheCat f={f} />
        </g>
        {f > 150 && (
          <text
            x={960}
            y={640}
            textAnchor="middle"
            fontSize={44}
            fontWeight="bold"
            fill={PAL.cream}
            opacity={0.9}
            fontFamily={FONT.latin}
          >
            rendered by raea — no video models, just your GPU ♪
          </text>
        )}
      </svg>
    </AbsoluteFill>
  );
}
