# Fonts — licensing & free alternatives

## TL;DR
- **Granola's brand fonts can't be downloaded/used by us legitimately.** Their display serif (**Quadrant**, the "Quadrant Notepad" cut) is bespoke/not retail; their UI sans (**Melange** = KMR Melange Grotesk) is a paid retail font from Kimera. There is **no legitimate free download** of either — ignore the "free font" piracy sites.
- **What this design system actually ships:** free **OFL** fonts that lead the same stacks — **Fraunces** (display serif), **Hanken Grotesk** (body/UI sans), **JetBrains Mono** (code). Free to self-host and embed commercially.

> Naming note: Granola's [own brand post](https://www.granola.ai/blog/a-new-look-for-granola) names the pair **"Quadrant"** (a *slightly mechanical slab serif* for display) + **"Melange"** (a neutral, subtly characterful UI sans). "Quadrant Notepad" — the family name we read from their live CSS (`--font-display`) — is an internal/custom cut of Quadrant. The font stacks keep the exact `"Quadrant Notepad"` / `"KMR Melange Grotesk"` names first, so a licensed install renders identically; everyone else falls through to the free alternatives.

---

## A. The brand fonts — can we license/download them?

### KMR Melange Grotesk (the UI sans) — licensable, paid
- **Foundry:** Kimera Corp (Michael Clasen). Sold direct.
- **Buy:** [kimeracorp.eu/typefaces/melange-grotesk](https://kimeracorp.eu/typefaces/melange-grotesk) (also on [MyFonts](https://www.myfonts.com/collections/melange-font-calamar/)). 26 cuts (Thin→Extra Black + italics), otf/ttf/woff/woff2.
- **Trial:** the product page offers a watermarked/dev **trial** (not for production).
- **Price/tiers:** **TBD** — separate Desktop / Web / App licenses, gated behind the foundry cart; confirm there before quoting.
- **Self-host:** allowed **only** under a paid **webfont** license (gives you the `.woff2` within a pageview cap). Not freely redistributable.
- Sources: [Kimera](https://kimeracorp.eu/typefaces/melange-grotesk) · [Typecache](https://typecache.com/news/5964/) · [Fonts In Use](https://fontsinuse.com/typefaces/233306/melange-grotesk)

### Quadrant / "Quadrant Notepad" (the display serif) — bespoke, not retail
- **Foundry:** Matter of Sorts (Vincent Chan, Melbourne). Public family is **Quadrant Text**.
- **Availability:** "made available on request, but never officially released" as a retail product — licensed by request / for bespoke brand work. **The "Quadrant Notepad" cut Granola uses is custom/exclusive and we cannot license it.**
- **To inquire (bespoke only):** mail@matterofsorts.com — treat as unavailable by default.
- Sources: [Typewolf](https://www.typewolf.com/quadrant-text) · [Matter of Sorts](https://matterofsorts.com/) · [Fonts In Use](https://fontsinuse.com/typefaces/230206/quadrant-text)

### ⚠️ Piracy warning
Sites like cdnfonts / cufonfonts / ifonts / freefonts.io list "Quadrant" or "Melange" as free downloads. **These are unlicensed redistributions — do not use them.** The only lawful paths are: pay Kimera for Melange, or contact Matter of Sorts for Quadrant (custom). Do not self-host either without a license.

---

## B. Free alternatives (what we ship — all OFL 1.1)

| Role | Brand font | Free substitute (Google Fonts) | Why it's the closest |
| --- | --- | --- | --- |
| Display | Quadrant (mechanical slab serif) | **Fraunces** | Only Google Font with that warm, characterful, slightly-quirky Clarendon/display energy; optical sizing + "wonky"/SOFT axes, built for headlines. Backup: **Newsreader** (more a refined reading serif); **Source Serif 4** (neutral, least display character). |
| Body / UI | Melange (warm neo-grotesque) | **Hanken Grotesk** | "Inspired by the classic grotesques" — warm, subtly humanist neo-grotesque, the best match for Melange's "neutral but characterful." Backup: **Manrope** (cooler/geometric); **Inter** (safe but clinical); avoid **Space Grotesk** (too techy/geometric). |
| Code | JetBrains Mono | **JetBrains Mono** | Same font — already free. |

All three are **SIL Open Font License 1.1**: free for commercial use, self-hosting and embedding allowed.
Sources: [Fraunces](https://fonts.google.com/specimen/Fraunces) · [Hanken Grotesk](https://fonts.google.com/specimen/Hanken+Grotesk) · [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono)

---

## C. How to download / load the free fonts

### Option 1 — Google Fonts CDN (what `examples/index.html` uses)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
```

### Option 2 — Self-host (recommended for production: no third-party dependency, faster, privacy)
1. **Download `.woff2`** the easy way via **google-webfonts-helper** ([gwfh.mranftl.com](https://gwfh.mranftl.com/)): pick family → weights 400/500/600/700 → `latin` → **woff2** → download zip (includes a ready `@font-face` snippet). Or grab official sources from the repos: [Fraunces](https://github.com/undercasetype/Fraunces) · [Hanken Grotesk](https://github.com/marcologous/hanken-grotesk) · [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) — and **keep each `OFL.txt`**.
   ```bash
   # example: fetch Hanken Grotesk woff2 (latin) as a zip
   curl -L "https://gwfh.mranftl.com/api/fonts/hanken-grotesk?download=zip&subsets=latin&variants=regular,500,600,700&formats=woff2" -o hanken-grotesk.zip
   ```
2. **Drop the files** in `design-system/examples/fonts/` (or your app's `/public/fonts`).
3. **Declare `@font-face`** (variable-font form shown; or one rule per static weight):
   ```css
   @font-face {
     font-family: "Hanken Grotesk";
     font-style: normal;
     font-weight: 400 700;        /* variable range */
     font-display: swap;
     src: url("/fonts/hanken-grotesk.woff2") format("woff2");
   }
   ```
   The font-family names already match the stacks in `tokens.css` / `tailwind-preset.js`, so no other change is needed.

### OFL compliance (do this when self-hosting)
The OFL **permits** bundling, embedding, self-hosting, and redistribution — including commercially — provided you: (1) **ship the `OFL.txt`** license file with the fonts, (2) **don't sell the fonts on their own**, and (3) **don't reuse the reserved font name** on a modified version. Hosting them as webfonts on our own server is fully allowed.

---

## Bottom line
- **Brand-exact (Granola):** license **Melange** from Kimera (paid, price TBD); **Quadrant** is bespoke and effectively unobtainable. Never pirate.
- **Ship now (free):** **Fraunces + Hanken Grotesk + JetBrains Mono** — already wired into the stacks; self-host per Option 2 for production.
