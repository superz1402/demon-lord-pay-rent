import { PAL, blink, mouthFlap } from "../style";

/**
 * KENJI TANAKA, 26 — UX designer, straight man (tsukkomi), keeper of
 * The Rent Envelope. Chronically 12% stressed. Panic is his default state.
 */
export function Kenji({
  f,
  talking = false,
  panic = true,
  scale = 1,
  x = 0,
  y = 0,
  withEnvelope = true,
}: {
  f: number;
  talking?: boolean;
  panic?: boolean;
  scale?: number;
  x?: number;
  y?: number;
  withEnvelope?: boolean;
}) {
  const shake = panic ? Math.sin(f / 2.2) * 2.5 : Math.sin(f / 16) * 3;
  const open = mouthFlap(f, talking);
  const shut = blink(f);

  return (
    <g
      transform={`translate(${x},${y + shake}) scale(${scale})`}
      stroke={PAL.ink}
      strokeWidth={7}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      {/* hoodie body */}
      <path
        d="M -80 260 C -88 130 -60 70 0 62 C 60 70 88 130 80 260 Z"
        fill={PAL.kenjiHood}
      />
      {/* hood rim + drawstrings */}
      <path d="M -46 74 Q 0 108 46 74" fill="none" />
      <path d="M -14 92 L -18 130" fill="none" strokeWidth={5} />
      <path d="M 14 92 L 18 130" fill="none" strokeWidth={5} />

      {/* head */}
      <g transform="translate(0,-40)">
        {/* hair */}
        <path
          d="M -62 -30 C -70 -96 -30 -118 0 -118 C 30 -118 70 -96 62 -30 C 52 -66 44 -74 34 -58 C 24 -86 10 -92 0 -64 C -10 -92 -24 -86 -34 -58 C -44 -74 -52 -66 -62 -30 Z"
          fill={PAL.kenjiHair}
        />
        <rect x={-52} y={-44} width={104} height={102} rx={34} fill={PAL.kenjiSkin} />
        {/* stress vein — sitcom staple */}
        {panic && (
          <path
            d="M 40 -66 q 8 -14 0 -22 q -8 8 0 22 Z"
            fill={PAL.accent}
            strokeWidth={4}
          />
        )}

        {/* eyes — wide with despair */}
        {shut ? (
          <>
            <path d="M -38 -6 Q -26 2 -14 -6" fill="none" />
            <path d="M 14 -6 Q 26 2 38 -6" fill="none" />
          </>
        ) : (
          <>
            <ellipse cx={-26} cy={-4} rx={13} ry={panic ? 17 : 13} fill="#fff" />
            <ellipse cx={26} cy={-4} rx={13} ry={panic ? 17 : 13} fill="#fff" />
            <circle cx={-26} cy={-4} r={5.5} fill={PAL.ink} stroke="none" />
            <circle cx={26} cy={-4} r={5.5} fill={PAL.ink} stroke="none" />
          </>
        )}
        {/* eyebags — 3 months of this */}
        <path d="M -36 12 Q -26 16 -16 12" fill="none" strokeWidth={4} />
        <path d="M 16 12 Q 26 16 36 12" fill="none" strokeWidth={4} />

        {/* mouth */}
        {open ? (
          <ellipse cx={0} cy={34} rx={16} ry={12} fill={PAL.ink} />
        ) : (
          <path d="M -12 34 Q 0 30 12 34" fill="none" />
        )}
      </g>

      {/* arms — one thrust out with the envelope */}
      {withEnvelope ? (
        <>
          <path d="M -70 130 Q -80 190 -60 220" fill="none" />
          <path d="M 70 130 Q 130 110 168 96" fill="none" />
          {/* THE ENVELOPE (tm) */}
          <g transform="translate(196,86) rotate(-12)">
            <rect x={-46} y={-30} width={92} height={60} rx={6} fill={PAL.paper} />
            <path d="M -46 -30 L 0 8 L 46 -30" fill="none" strokeWidth={5} />
            <circle cx={34} cy={16} r={12} fill={PAL.accent} strokeWidth={4} />
            <text
              x={34}
              y={22}
              textAnchor="middle"
              fontSize={16}
              fontWeight="bold"
              fill="#fff"
              stroke="none"
              fontFamily="'Noto Sans JP',sans-serif"
            >
              家賃
            </text>
          </g>
        </>
      ) : (
        <>
          <path d="M -70 130 Q -80 190 -60 220" fill="none" />
          <path d="M 70 130 Q 80 190 60 220" fill="none" />
        </>
      )}
    </g>
  );
}
