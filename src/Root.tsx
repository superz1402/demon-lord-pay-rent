import { Composition, AbsoluteFill, registerRoot } from "raea";
import { FPS, WIDTH, HEIGHT, DUR } from "./style";
import { ColdOpen } from "./scenes/ColdOpen";
import { Op } from "./scenes/Op";
import { Eyecatch } from "./scenes/Eyecatch";
import { EndCard } from "./scenes/EndCard";

/**
 * Composition registry for DEMON LORD, PAY RENT!
 * Episode 1 pilot package = 4 pieces (cold open / OP / eyecatch / end card),
 * rendered individually and concatenated (see README) — this keeps each
 * piece independently re-renderable while you iterate on jokes.
 */
export function Root() {
  return (
    <AbsoluteFill>
      {/* registry placeholder — real entries below */}
    </AbsoluteFill>
  );
}

export const compositions = [
  { id: "cold-open", component: ColdOpen, durationInFrames: DUR.coldOpen },
  { id: "op", component: Op, durationInFrames: DUR.op },
  { id: "eyecatch", component: Eyecatch, durationInFrames: DUR.eyecatch },
  { id: "end-card", component: EndCard, durationInFrames: DUR.endCard },
] as const;

/**
 * raea (canary) registry shape may want <Composition id component fps width height />.
 * If your build's `raea guide` shows that form, swap the default export for:
 *
 * registerRoot(() => (
 *   <>
 *     <Composition id="cold-open" component={ColdOpen} durationInFrames={DUR.coldOpen} fps={FPS} width={WIDTH} height={HEIGHT} />
 *     <Composition id="op" component={Op} durationInFrames={DUR.op} fps={FPS} width={WIDTH} height={HEIGHT} />
 *     <Composition id="eyecatch" component={Eyecatch} durationInFrames={DUR.eyecatch} fps={FPS} width={WIDTH} height={HEIGHT} />
 *     <Composition id="end-card" component={EndCard} durationInFrames={DUR.endCard} fps={FPS} width={WIDTH} height={HEIGHT} />
 *   </>
 * ));
 */
export default Root;
