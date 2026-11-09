import { AbsoluteFill, useCurrentFrame } from "raea";
import { PAL, FONT, DUR } from "../style";
import { Xargoth } from "../characters/Xargoth";
import { SeniorTheCat } from "../characters/SeniorTheCat";
import { SpeedLines } from "../Fx";

/**
 * EYECATCH — chibi bumper, 150 frames (5s).
 * "A-PART END / SEE YOU AFTER THE BREAK" with bouncing chibis and a jingle.
 */
export function Eyecatch() {
  const f = useCurrentFrame();

  // alternating bounce (classic eyecatch rhythm)
  const bounceA = Math.abs(Math.sin(f / 7)) * 26;
  const bounceB = Math.abs(Math.sin(f / 7 + Math.PI / 2)) * 26;

  return (
    <AbsoluteFill style={{ background: PAL.cream }}>
      <SpeedLines f={f} opacity={0.18} />
      <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{ display: "block" }}>
        {/* giant chibi bounce shadow */}
        <ellipse cx={620} cy={880} rx={190} ry={26} fill={PAL.ink} opacity={0.18} stroke="none" />
        <ellipse cx={1300} cy={880} rx={150} ry={22} fill={PAL.ink} opacity={0.18} stroke="none" />

        <g transform={`translate(620,${700 - bounceA}) scale(0.85)`}>
          <Xargoth f={f} emotion="sparkle" />
        </g>
        <g transform={`translate(1300,${760 - bounceB}) scale(0.8)`}>
          <SeniorTheCat f={f} sparkle />
        </g>

        {/* jingle dots */}
        {[0, 1, 2].map((i) => (
          <circle
            key={i}
            cx={960 + (i - 1) * 70}
            cy={210}
            r={16}
            fill={PAL.accent}
            opacity={Math.sin(f / 6 - i * 1.2) > 0 ? 1 : 0.25}
            stroke={PAL.ink}
            strokeWidth={5}
          />
        ))}
      </svg>

      <div
        style={{
          position: "absolute",
          top: 96,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: FONT.display,
          fontWeight: 900,
          fontSize: 72,
          color: PAL.ink,
        }}
      >
        Ａパート終了
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 110,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: FONT.latin,
          fontWeight: 900,
          fontSize: 54,
          letterSpacing: 8,
          color: PAL.accent,
          WebkitTextStroke: `2px ${PAL.ink}`,
          transform: `rotate(${Math.sin(f / 12) * 1.5}deg)`,
        }}
      >
        SEE YOU AFTER THE BREAK!
      </div>
    </AbsoluteFill>
  );
}
