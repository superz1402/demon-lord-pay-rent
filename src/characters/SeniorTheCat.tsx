import { PAL, blink } from "../style";

/**
 * "SENIOR" — the cat. Definitely not the legendary hero who sealed
 * Xargoth 800 years ago. The halo is a "collar". Do not ask questions.
 * Tail sways with `f`; smugness is permanent.
 */
export function SeniorTheCat({
  f,
  scale = 1,
  x = 0,
  y = 0,
  sparkle = false,
}: {
  f: number;
  scale?: number;
  x?: number;
  y?: number;
  sparkle?: boolean;
}) {
  const tail = Math.sin(f / 10) * 14;
  const earTwitch = (f % 90) < 6 ? -6 : 0;
  const shut = blink(f);

  return (
    <g
      transform={`translate(${x},${y}) scale(${scale})`}
      stroke={PAL.ink}
      strokeWidth={6}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      {/* tail */}
      <path
        d={`M 60 10 C 110 ${-10 + tail * 0.3}, 120 ${-60 + tail}, 96 ${-74 + tail}`}
        fill="none"
        strokeWidth={16}
      />
      {/* body */}
      <ellipse cx={0} cy={30} rx={62} ry={44} fill={PAL.catFur} />
      {/* orange patches */}
      <path d="M -50 6 C -30 -18 4 -20 22 0 C 0 6 -22 12 -50 6 Z" fill={PAL.catPatch} strokeWidth={4} />

      {/* head */}
      <g transform="translate(-6,-34)">
        {/* ears */}
        <path d={`M -42 -12 L -34 ${-44 + earTwitch} L -8 -24 Z`} fill={PAL.catFur} />
        <path d="M 42 -12 L 34 -44 L 8 -24 Z" fill={PAL.catFur} />
        {/* inner ears */}
        <path d="M -34 -18 L -30 ${-36 + earTwitch} L -16 -22 Z" fill={PAL.accent} strokeWidth={3} />
        {/* face */}
        <ellipse cx={0} cy={0} rx={46} ry={38} fill={PAL.catFur} />
        {/* forehead patch */}
        <path d="M -14 -34 C -4 -40 8 -38 14 -30 C 4 -26 -6 -26 -14 -34 Z" fill={PAL.catPatch} strokeWidth={3} />

        {/* THE HALO (it's a collar. sure.) */}
        <ellipse
          cx={0}
          cy={-44}
          rx={30}
          ry={9}
          fill="none"
          stroke={PAL.halo}
          strokeWidth={7}
        />

        {/* eyes — smug half-lids forever */}
        {shut ? (
          <>
            <path d="M -30 -2 Q -22 4 -14 -2" fill="none" strokeWidth={5} />
            <path d="M 14 -2 Q 22 4 30 -2" fill="none" strokeWidth={5} />
          </>
        ) : (
          <>
            <ellipse cx={-22} cy={-2} rx={9} ry={11} fill={PAL.ink} stroke="none" />
            <ellipse cx={22} cy={-2} rx={9} ry={11} fill={PAL.ink} stroke="none" />
            <path d="M -32 -10 L -12 -6" fill={PAL.ink} strokeWidth={5} />
            <path d="M 12 -6 L 32 -10" fill={PAL.ink} strokeWidth={5} />
          </>
        )}
        {/* whiskers */}
        <path d="M -44 8 L -66 2 M -44 16 L -66 18" fill="none" strokeWidth={3} />
        <path d="M 44 8 L 66 2 M 44 16 L 66 18" fill="none" strokeWidth={3} />
        {/* :3 mouth */}
        <path d="M -8 16 Q -4 20 0 16 Q 4 20 8 16" fill="none" strokeWidth={4} />
      </g>

      {/* front paws tucked */}
      <path d="M -30 62 Q -20 70 -6 62" fill="none" strokeWidth={5} />
      <path d="M 6 62 Q 20 70 30 62" fill="none" strokeWidth={5} />

      {/* hero aura sparkles */}
      {sparkle && (
        <g stroke="none" fill={PAL.halo}>
          <path d="M 90 -70 l 5 14 14 5 -14 5 -5 14 -5 -14 -14 -5 14 -5 Z" />
          <path d="M -96 -40 l 4 11 11 4 -11 4 -4 11 -4 -11 -11 -4 11 -4 Z" />
          <path d="M 70 60 l 3 9 9 3 -9 3 -3 9 -3 -9 -9 -3 9 -3 Z" />
        </g>
      )}
    </g>
  );
}
