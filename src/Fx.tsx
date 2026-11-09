import { PAL, FONT, lerp } from "./style";

/** Rotating manga speed-line rays. density = number of rays. */
export function SpeedLines({
  f,
  density = 28,
  opacity = 0.85,
  cx = 960,
  cy = 540,
}: {
  f: number;
  density?: number;
  opacity?: number;
  cx?: number;
  cy?: number;
}) {
  const rot = (f * 1.2) % (360 / density);
  const rays = Array.from({ length: density }, (_, i) => {
    const a = ((i * 360) / density + rot) * (Math.PI / 180);
    const r1 = 260;
    const r2 = 1400;
    return (
      <line
        key={i}
        x1={cx + Math.cos(a) * r1}
        y1={cy + Math.sin(a) * r1}
        x2={cx + Math.cos(a) * r2}
        y2={cy + Math.sin(a) * r2}
        stroke={PAL.speed}
        strokeWidth={i % 2 === 0 ? 26 : 10}
        opacity={i % 2 === 0 ? opacity : opacity * 0.5}
      />
    );
  });
  return <g>{rays}</g>;
}

/** Floating menace glyphs (ゴゴゴ...), the universal "oh no" of anime. */
export function MenaceGlyphs({
  f,
  x = 0,
  y = 0,
  chars = ["ゴ", "ゴ", "ゴ"],
  color = PAL.ink,
}: {
  f: number;
  x?: number;
  y?: number;
  chars?: string[];
  color?: string;
}) {
  return (
    <g transform={`translate(${x},${y})`}>
      {chars.map((c, i) => {
        const t = (f / 40 + i * 0.33) % 1;
        return (
          <text
            key={i}
            x={i * 58}
            y={-t * 60}
            fontSize={64}
            fontWeight="black"
            fill={color}
            opacity={0.9 - t * 0.5}
            fontFamily={FONT.display}
            stroke="none"
          >
            {c}
          </text>
        );
      })}
    </g>
  );
}

/** Impact burst — ドン! Comedic punctuation. */
export function ImpactDon({
  f,
  t0,
  x = 960,
  y = 420,
}: {
  f: number;
  t0: number;
  x?: number;
  y?: number;
}) {
  const t = f - t0;
  if (t < 0 || t > 22) return null;
  const grow = lerp(0.4, 1.25, Math.min(1, t / 6));
  const fade = t > 16 ? 1 - (t - 16) / 6 : 1;
  return (
    <g transform={`translate(${x},${y}) scale(${grow})`} opacity={fade}>
      {Array.from({ length: 12 }, (_, i) => {
        const a = ((i * 360) / 12 + 15) * (Math.PI / 180);
        return (
          <path
            key={i}
            d={`M ${Math.cos(a) * 150} ${Math.sin(a) * 150} L ${Math.cos(a + 0.09) * 260} ${Math.sin(a + 0.09) * 260} L ${Math.cos(a + 0.18) * 150} ${Math.sin(a + 0.18) * 150} Z`}
            fill={PAL.crown}
            stroke={PAL.ink}
            strokeWidth={6}
          />
        );
      })}
      <text
        x={0}
        y={26}
        textAnchor="middle"
        fontSize={120}
        fontWeight="black"
        fill={PAL.accent}
        stroke={PAL.ink}
        strokeWidth={8}
        fontFamily={FONT.display}
      >
        ドン
      </text>
    </g>
  );
}

/** Sitcom laugh-beat card — yellow "HA HA HA" wipe with audience silhouettes. */
export function LaughCard({ f, t0, len = 24 }: { f: number; t0: number; len?: number }) {
  const t = f - t0;
  if (t < 0 || t > len) return null;
  const inT = Math.min(1, t / 5);
  const outT = t > len - 5 ? (len - t) / 5 : 1;
  const scale = lerp(0.6, 1, inT);
  return (
    <g opacity={Math.min(inT, outT)}>
      <rect x={0} y={880} width={1920} height={200} fill={PAL.laugh} stroke={PAL.ink} strokeWidth={8} />
      <g transform={`translate(960,980) scale(${scale})`}>
        {["HA", "HA", "HA"].map((h, i) => (
          <text
            key={i}
            x={(i - 1) * 260}
            y={-Math.abs(i - 1) * 34 + 24}
            textAnchor="middle"
            fontSize={96}
            fontWeight="black"
            fill={PAL.ink}
            fontFamily={FONT.latin}
            stroke="none"
            transform={`rotate(${(i - 1) * -8})`}
          >
            {h}
          </text>
        ))}
      </g>
    </g>
  );
}

/** Subtitle bar — dual-language sitcom dialogue caption. */
export function Subtitle({
  f,
  t0,
  t1,
  speaker,
  en,
  jp,
  color = PAL.cream,
}: {
  f: number;
  t0: number;
  t1: number;
  speaker: string;
  en: string;
  jp?: string;
  color?: string;
}) {
  if (f < t0 || f > t1) return null;
  const inT = Math.min(1, (f - t0) / 6);
  return (
    <g opacity={inT}>
      <rect x={260} y={906} width={1400} height={118} rx={14} fill={PAL.ink} opacity={0.82} stroke="none" />
      <rect x={260} y={906} width={14} height={118} rx={7} fill={color} stroke="none" />
      <text x={306} y={958} fontSize={40} fontWeight="black" fill={color} fontFamily={FONT.latin} stroke="none">
        {speaker}
      </text>
      <text x={306} y={1004} fontSize={34} fill="#FFFFFF" fontFamily={FONT.body} stroke="none">
        {en}
      </text>
      {jp && (
        <text x={1620} y={958} textAnchor="end" fontSize={30} fontWeight="bold" fill={color} opacity={0.85} fontFamily={FONT.display} stroke="none">
          {jp}
        </text>
      )}
    </g>
  );
}
