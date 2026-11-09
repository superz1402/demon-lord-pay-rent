/**
 * DEMON LORD, PAY RENT! — Style Bible & Timing Constants
 * -------------------------------------------------------
 * Flat cel-shaded anime sitcom look: thick ink outlines, two-tone shadows,
 * comedy SFX glyphs (ゴゴゴ / ドン), speed lines, letterboxed 16:9.
 *
 * Frame math helpers here are self-contained on purpose: they only rely on
 * plain arithmetic so the scenes compile on any raea build.
 */

export const FPS = 30;

export const WIDTH = 1920;
export const HEIGHT = 1080;

/** Scene durations in frames (30 fps). */
export const DUR = {
  coldOpen: 600, // 20s
  op: 540, // 18s
  eyecatch: 150, // 5s
  endCard: 240, // 8s
};

/** Core palette — "warm apartment amber vs. demon purple". */
export const PAL = {
  ink: "#1D1626", // outlines, text
  cream: "#FFF6E5", // card backgrounds
  paper: "#F7E8C9", // envelope, warm paper
  roomWall: "#4A3B63", // apartment wall (night)
  roomFloor: "#2B2138", // apartment floor
  lamp: "#FFB65C", // warm lamp glow
  window: "#1A2440", // night city window
  windowCity: "#31406B",
  xarSkin: "#9FDFB6", // demon-lord green
  xarCape: "#5B2A86", // demon purple
  xarHair: "#2A1240",
  crown: "#F5C542", // tiny crown gold
  kenjiHood: "#3E7CB1", // roommate blue hoodie
  kenjiHair: "#2E2A32",
  kenjiSkin: "#F3C89E",
  catFur: "#F2E9DC", // the hero-cat cream
  catPatch: "#E8874A", // orange patches
  halo: "#FFE066", // "collar" that is definitely a halo
  accent: "#FF5A4E", // title red-orange
  laugh: "#FFD23F", // laugh-beat card yellow
  demonFire: "#B45CFF", // snap-flame purple
  speed: "#FFFFFF",
};

/** Base font stacks — JP glyphs fall back to system anime-safe fonts. */
export const FONT = {
  display:
    "'Noto Sans JP','Hiragino Sans','Yu Gothic','Noto Sans SC',sans-serif",
  body: "'Noto Sans JP','Hiragino Sans','Yu Gothic',sans-serif",
  latin: "'Inter','Helvetica Neue',Arial,sans-serif",
};

/* ------------------------------------------------------------------ */
/* Frame math — tiny, dependency-free easing/range helpers             */
/* ------------------------------------------------------------------ */

export const clamp = (v: number, a: number, b: number) =>
  Math.min(b, Math.max(a, v));

/** 0→1 progress of frame f inside [a,b], clamped. */
export const prog = (f: number, a: number, b: number) =>
  clamp((f - a) / (b - a), 0, 1);

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
export const easeIn = (t: number) => t * t * t;
export const easeInOut = (t: number) =>
  t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

/** Comedic punch-in overshoot: pops past 1 then settles. */
export const popOvershoot = (t: number) => {
  const c = 1.70158 + 1;
  return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2);
};

/** Simple 2-frame mouth flap: true on even frames. */
export const mouthFlap = (f: number, talking: boolean) =>
  talking && f % 6 < 3;

/** Blink: brief eye-shut windows roughly every 2.4s. */
export const blink = (f: number) => {
  const c = f % 72;
  return c > 64 && c < 68;
};

/** Sitcom laugh-beat marker: show "HA HA HA" card for N frames. */
export const isLaughBeat = (f: number, start: number, len = 24) =>
  f >= start && f < start + len;
