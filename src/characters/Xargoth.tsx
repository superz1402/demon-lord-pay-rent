import { PAL, blink, mouthFlap } from "../style";

export type Emotion = "smug" | "panic" | "idle" | "sparkle";

/**
 * XARGOTH THE UNENDING — Demon Lord (self-proclaimed), tenant (actual).
 * Green skin, towering purple hair, tiny tilted crown, high-collar cape.
 * Drawn flat-cel with thick ink outlines. `f` drives idle bob / blink / mouth.
 */
export function Xargoth({
  f,
  emotion = "smug",
  talking = false,
  scale = 1,
  x = 0,
  y = 0,
}: {
  f: number;
  emotion?: Emotion;
  talking?: boolean;
  scale?: number;
  x?: number;
  y?: number;
}) {
  const bob = Math.sin(f / 14) * 4;
  const open = mouthFlap(f, talking);
  const shut = blink(f);
  const panic = emotion === "panic";

  const eyeLidY = panic ? -14 : emotion === "smug" ? 6 : 0;

  return (
    <g
      transform={`translate(${x},${y + bob}) scale(${scale})`}
      stroke={PAL.ink}
      strokeWidth={7}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      {/* cape body */}
      <path
        d="M -95 260 C -120 120 -90 30 0 18 C 90 30 120 120 95 260 Z"
        fill={PAL.xarCape}
      />
      {/* high collar */}
      <path d="M -78 60 L -46 -14 L -10 46 Z" fill={PAL.xarCape} />
      <path d="M 78 60 L 46 -14 L 10 46 Z" fill={PAL.xarCape} />
      {/* chest skin */}
      <path d="M -44 250 L -44 96 Q 0 70 44 96 L 44 250 Z" fill={PAL.xarSkin} />
      {/* royal medallion (rent unpaid badge) */}
      <circle cx={0} cy={130} r={20} fill={PAL.crown} />
      <text
        x={0}
        y={140}
        textAnchor="middle"
        fontSize={24}
        fontFamily="'Noto Sans JP',sans-serif"
        fill={PAL.ink}
        stroke="none"
        fontWeight="bold"
      >
        滞
      </text>

      {/* head */}
      <g transform="translate(0,-60)">
        {/* hair mass behind */}
        <path
          d="M -105 -10 C -130 -110 -70 -170 0 -170 C 70 -170 130 -110 105 -10 C 80 -60 60 -70 40 -40 L 30 -90 L 0 -40 L -30 -90 L -40 -40 C -60 -70 -80 -60 -105 -10 Z"
          fill={PAL.xarHair}
        />
        {/* horns */}
        <path d="M -78 -104 C -96 -150 -88 -176 -58 -178 C -66 -156 -66 -138 -56 -118 Z" fill="#FFF3DC" />
        <path d="M 78 -104 C 96 -150 88 -176 58 -178 C 66 -156 66 -138 56 -118 Z" fill="#FFF3DC" />
        {/* tiny tilted crown */}
        <g transform="translate(10,-160) rotate(14)">
          <path d="M -26 14 L -26 -8 L -12 2 L 0 -14 L 12 2 L 26 -8 L 26 14 Z" fill={PAL.crown} />
        </g>
        {/* face */}
        <rect x={-64} y={-58} width={128} height={120} rx={44} fill={PAL.xarSkin} />
        {/* ears */}
        <path d="M -64 -6 L -92 -20 L -62 22 Z" fill={PAL.xarSkin} />
        <path d="M 64 -6 L 92 -20 L 62 22 Z" fill={PAL.xarSkin} />

        {/* eyes */}
        {shut ? (
          <>
            <path d="M -46 -2 Q -32 8 -18 -2" fill="none" />
            <path d="M 18 -2 Q 32 8 46 -2" fill="none" />
          </>
        ) : (
          <>
            <ellipse cx={-32} cy={-2} rx={15} ry={panic ? 20 : 15} fill="#fff" />
            <ellipse cx={32} cy={-2} rx={15} ry={panic ? 20 : 15} fill="#fff" />
            <circle cx={-32} cy={-2 + eyeLidY * 0.4} r={6} fill={PAL.ink} stroke="none" />
            <circle cx={32} cy={-2 + eyeLidY * 0.4} r={6} fill={PAL.ink} stroke="none" />
            {/* smug lids */}
            {emotion === "smug" && (
              <path d="M -50 -12 L -16 -4" fill="none" strokeWidth={9} />
            )}
            {emotion === "smug" && <path d="M 16 -4 L 50 -12" fill="none" strokeWidth={9} />}
          </>
        )}

        {/* brows */}
        {panic ? (
          <>
            <path d="M -50 -26 L -18 -32" fill="none" />
            <path d="M 18 -32 L 50 -26" fill="none" />
          </>
        ) : (
          <>
            <path d="M -50 -24 L -18 -28" fill="none" />
            <path d="M 18 -28 L 50 -24" fill="none" />
          </>
        )}

        {/* mouth */}
        {open ? (
          <path d="M -22 34 Q 0 58 22 34 Q 0 46 -22 34 Z" fill={PAL.ink} />
        ) : emotion === "smug" ? (
          <path d="M -20 36 Q 0 50 24 34" fill="none" />
        ) : panic ? (
          <ellipse cx={0} cy={40} rx={14} ry={10} fill={PAL.ink} />
        ) : (
          <path d="M -16 38 Q 0 44 16 38" fill="none" />
        )}

        {/* tiny fangs */}
        <path d="M -10 38 L -6 46 L -2 38 Z" fill="#fff" strokeWidth={3} />
        <path d="M 12 38 L 16 46 L 20 38 Z" fill="#fff" strokeWidth={3} />

        {/* panic sweat */}
        {panic && (
          <g stroke="none">
            <path
              d="M 74 -40 q 10 16 0 24 q -10 -8 0 -24 Z"
              fill="#7FD4FF"
              stroke={PAL.ink}
              strokeWidth={4}
            />
          </g>
        )}
      </g>

      {/* arms crossed, regal */}
      <path d="M -70 140 Q -30 120 -6 150" fill="none" />
      <path d="M 70 140 Q 30 120 6 150" fill="none" />
    </g>
  );
}
