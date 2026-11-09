# 「魔王、家賃を払え！」DEMON LORD, PAY RENT!
### Episode 1 — “The Rent Must Flow” · Director's Beat Sheet & Script

> Direction philosophy (borrowed from lemo-opuscar): **direct, don't generate.**
> Every shot is drawn in code, framed on purpose, and timed to a laugh beat.
> Flat cel look, two-tone shadows, thick ink outlines. The couch never moves.

---

## The Show

| | |
|---|---|
| **Title** | 魔王、家賃を払え！ / *DEMON LORD, PAY RENT!* |
| **Format** | Anime sitcom, single apartment set, 3–5 min episodes |
| **Engine** | Each episode = cold open (20s) + OP (18s) + A/B parts + eyecatch (5s) + end card (8s) |
| **Comedy engine** | One mundane problem × the Demon Lord's grandiosity × Kenji's despair. Cat judges silently. |

## The Cast

| Character | Role | Voice in one line |
|---|---|---|
| **魔王ザルゴス** Xargoth the Unending | Conqueror of 108 worlds. Tenant of apartment 302. Behind on rent. | “Fiat currency is beneath me. So is your WiFi password.” |
| **田中ケンジ** Kenji Tanaka, 26 | UX designer, roommate, keeper of The Rent Envelope™. | “You turned my security deposit into a *dragon*. That was the deposit.” |
| **シニア** “Senior” (the cat) | The hero who sealed Xargoth 800 years ago. Won't confirm. Also freeloads. | “meow.” (Subtitled: *“I could fix this. I choose not to.”*) |
| **大家のオバアさん** Landlord Obaa-san (Ep. 2+) | Clearly stronger than the Demon Lord. Carries a giant keyring. | “Rent. Is due. Little king.” |

**Why it's funny forever:** rent day is monthly → infinite episodes. Every episode's
cold open ends with the freeze-frame + record-scratch + cat narrating the debt.

---

## Episode 1 structure (this repo renders the bold pieces)

| Piece | Duration | Frames @30fps | Status |
|---|---|---|---|
| **Cold open** | 20s | 600 | ✅ `src/scenes/ColdOpen.tsx` |
| **OP title sequence** | 18s | 540 | ✅ `src/scenes/Op.tsx` |
| A-part (Ep. 1 script below) | ~90s | — | 📝 script only |
| **Eyecatch** | 5s | 150 | ✅ `src/scenes/Eyecatch.tsx` |
| B-part (script only) | ~90s | — | 📝 script only |
| **End card** | 8s | 240 | ✅ `src/scenes/EndCard.tsx` |

---

## COLD OPEN — “The Rent Must Flow” (shot list)

| # | Frames | Shot | Action / dialogue | Comedy note |
|---|--------|------|-------------------|-------------|
| 1 | 0–60 | Establishing, slow L pan | Apartment 302 at night. City twinkles. “COLD OPEN” chip. | ザワ… ambient dread |
| 2 | 60–160 | Medium on Xargoth, sofa | XARGOTH: “I have conquered 108 worlds. Conquering a landlord? ...The logistics elude me.” | ゴゴゴ aura; **laugh beat @140** |
| 3 | 160–300 | Kenji slides in, punch-in | KENJI: “XARGOTH. Rent day. THREE. MONTHS.” | ドン impact @240; **laugh @272** |
| 4 | 300–430 | Two-shot, snap | Xargoth snaps — envelope becomes IOU confetti. XARGOTH: “Behold. Economics.” | チッ; **laugh @400** |
| 5 | 430–565 | Hard zoom → FREEZE on cat | SENIOR: “Yep. You're wondering how a demon lord got ¥284,000 behind on rent.” | Record scratch ♪; **laugh @540** |
| 6 | 565–600 | SMASH CUT | Title card slams in with speed lines. | ドン |

## OP — beat map (18s)

| Frames | Beat |
|--------|------|
| 0–40 | Logo slam 「魔王、家賃を払え！」 over speed lines |
| 40–150 | XARGOTH card — “Rent status: FIAT CURRENCY IS BENEATH ME” |
| 150–250 | KENJI card — “Rent status: PAYING FOR TWO” |
| 250–340 | CAT card — “Definitely not the hero of legend.” |
| 340–470 | Group shot at the kotatsu; the sacred envelope levitates; coins + sakura fall |
| 470–540 | Title finale + parody credits: *Screenplay — THE CAT · Music — CONVENIENCE STORE SPEAKERS · Catering — 100 YEN SHOP* |

---

## A-PART — “Three Months, Three Excuses” (script)

1. **Cold open aftermath.** Kenji holds a bag of IOU notes. Obaa-san's shadow appears
   under the door — the keyring rattles like a horror sting. Xargoth hides behind
   the cat. The cat does not move. Xargoth: “The small one will protect me.”
2. **Excuse #1 — Currency.** Xargoth presents a chest of “gold”: conbini gift points.
   KENJI: “This is 3,000 points at Tasty Mart.” XARGOTH: “A treasury.”
3. **Excuse #2 — Diplomacy.** Xargoth declares the apartment “sovereign territory.”
   The cat immediately pees in the corner to contest the border. Subtitled cat:
   *“Treaties require signatures. I've marked mine.”*
4. **Excuse #3 — Employment.** Kenji gets Xargoth a part-time interview at Tasty Mart.
   Xargoth lists “108 worlds” under experience. Manager: “Can you start Tuesday?”
   Xargoth, tearing up, to the cat: “He kneels first... this shop kneels first...”

## B-PART — “The Overtime of Darkness” (script)

1. Xargoth's first shift. He restocks onigiri like it's siege logistics.
   Power-trip montage; the store has never been more efficient.
2. Customer complaint: no more limited-edition pudding. Xargoth declares war on
   the customer. Kenji, off-screen: “THE CUSTOMER IS A ALLY, NOT A GOBLIN.”
3. Payday: ¥46,000 in an envelope. Xargoth holds his first earned money.
   Long silence. XARGOTH: “...So this is what the peasants feel.” Cat subtitled:
   *“Character growth. Disgusting.”*
4. **Tag:** he hands ALL of it to Obaa-san. Obaa-san: “Three months is ¥284,000,
   little king.” Xargoth: “...I have conquered 108 worlds.” Obaa-san simply
   *looks at him.* Xargoth pays. Freeze. CAT: “meow.” **→ Eyecatch → End card.**

---

## Style bible (for consistency across episodes)

- **Palette:** night-purple walls `#4A3B63`, floor `#2B2138`, lamp amber `#FFB65C`,
  demon purple `#5B2A86`, accent red-orange `#FF5A4E`, laugh-card yellow `#FFD23F`.
- **Rendering rules:** flat fills, ONE two-tone shadow max, 6–8px ink outlines,
  no gradients except lamp glow. Sitcom blocking: sofa (Xargoth) / kotatsu (cat) /
  door (Kenji) never move.
- **SFX vocabulary:** ゴゴゴ (dread) · ドン (punchline) · チッ (annoyance) ·
  ピク (flinch) · ☆ (the cat's suspicious sparkle).
- **Laugh beats:** every joke lands on a yellow HA-HA wipe card — the anime
  equivalent of a laugh track, and it's rendered, not sampled.
