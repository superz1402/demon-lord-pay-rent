import { PAL } from "./style";

/**
 * The apartment set — tiny, slightly run-down, aggressively cozy.
 * Reused across scenes so blocking stays consistent (multi-cam sitcom rule:
 * the couch never moves; only the demon lord's dignity does).
 */
export function ApartmentSet({ f }: { f: number }) {
  // window city twinkle
  const tw = (i: number) => 0.35 + 0.3 * Math.sin(f / 20 + i * 1.7);
  const windows = Array.from({ length: 14 }, (_, i) => (
    <rect
      key={i}
      x={905 + (i % 7) * 46}
      y={212 + Math.floor(i / 7) * 60}
      width={20}
      height={26}
      fill={PAL.lamp}
      opacity={tw(i)}
      stroke="none"
    />
  ));

  return (
    <g stroke={PAL.ink} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round">
      {/* wall / floor */}
      <rect x={0} y={0} width={1920} height={1080} fill={PAL.roomWall} stroke="none" />
      <rect x={0} y={640} width={1920} height={440} fill={PAL.roomFloor} stroke="none" />
      <path d="M 0 640 L 1920 640" stroke={PAL.ink} strokeWidth={8} />

      {/* window with night city */}
      <rect x={860} y={140} width={420} height={330} rx={10} fill={PAL.window} />
      <rect x={860} y={140} width={420} height={330} rx={10} fill="none" strokeWidth={10} />
      <path d="M 1070 140 L 1070 470 M 860 305 L 1280 305" strokeWidth={8} />
      <g stroke="none">{windows}</g>

      {/* lamp */}
      <rect x={1560} y={430} width={16} height={220} fill="#6B5A45" />
      <path d="M 1500 430 L 1636 430 L 1600 340 L 1536 340 Z" fill={PAL.lamp} />
      <circle cx={1568} cy={420} r={170} fill={PAL.lamp} opacity={0.16} stroke="none" />

      {/* sofa (Xargoth's throne) */}
      <rect x={130} y={520} width={640} height={170} rx={26} fill="#7A4E8C" />
      <rect x={100} y={430} width={120} height={260} rx={22} fill="#8A5C9E" />
      <rect x={680} y={430} width={120} height={260} rx={22} fill="#8A5C9E" />
      <rect x={230} y={470} width={220} height={110} rx={18} fill="#9A6CAE" />
      <rect x={460} y={470} width={220} height={110} rx={18} fill="#9A6CAE" />

      {/* kotatsu table (front right) */}
      <rect x={1180} y={640} width={560} height={120} rx={16} fill="#B07A4A" />
      <rect x={1220} y={760} width={40} height={140} fill="#8A5C38" />
      <rect x={1660} y={760} width={40} height={140} fill="#8A5C38" />
      {/* kotatsu blanket */}
      <path d="M 1150 640 L 1770 640 L 1740 720 L 1180 720 Z" fill="#C0392B" opacity={0.9} stroke="none" />

      {/* scattered evidence of bad tenancy */}
      <path d="M 840 800 l 60 0 l -30 -46 Z" fill={PAL.paper} strokeWidth={4} />
      <text x={852} y={806} fontSize={30} fill={PAL.ink} stroke="none" fontFamily={FONT_BODY}>
        IOU
      </text>
      <circle cx={960} cy={840} r={16} fill={PAL.crown} strokeWidth={4} />
      <path d="M 300 850 q 30 -18 60 0 q -30 18 -60 0 Z" fill={PAL.paper} strokeWidth={4} />

      {/* curtains */}
      <path d="M 820 120 C 790 240 800 380 820 500 L 860 500 L 860 120 Z" fill="#6E2B5E" />
      <path d="M 1320 120 C 1350 240 1340 380 1320 500 L 1280 500 L 1280 120 Z" fill="#6E2B5E" />
    </g>
  );
}

const FONT_BODY = "'Noto Sans JP','Hiragino Sans',sans-serif";
