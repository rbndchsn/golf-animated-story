# Editing the motion comic

## Narrative

Edit `data/scenes.js`. Each scene is a JSON-like JavaScript object with these fields:

- `number`, `id`: stable scene index and deep-link target. Keep indices 1–43 if you merely edit text.
- `act`, `title`, `visual`: display metadata and illustrator reference.
- `quinn`, `vale`: visible dialogue. Aim for one concise, spoken sentence per character.
- `clue`: the visual reveal statement. It should clarify the scene's premise without presenting conjecture as documented fact.
- `status`: `FACT` (record), `LENS` (interpretation), `MIX` (both), or `OPEN` (unresolved).
- `detail`: expanded archival context revealed under `SOURCE & CONTEXT`.
- `sourceName`, `sourceUrl`: reference displayed in that panel. Public HTTPS URLs only if intentionally publishable.
- `svgFile`: path to the editable scene illustration.

You can modify a dialogue line without modifying any art or code. The standalone HTML must be rebuilt to reflect changes; the modular website reads `data/scenes.js` immediately.

## Illustrations

Every original comic scene has a full-resolution, vector-based SVG in `assets/illustrations/`. The SVGs can be opened in Inkscape, Illustrator, or text editor. Avoid renaming the two-digit numeric prefix (01-43). After changing an illustration, run:

```bash
python tools/sync_illustrations.py
python tools/build_standalone.py
```

The generated `data/illustrations.js` is a duplicate cache by design. It allows local double-clicking of `index.html` without the file permissions problems caused by fetching SVG assets under `file://`.

## Animation

- `css/animations.css`: transitions, gestures, sketch-line effects, and entrances.
- `js/motion.js`: SVG clue animations for the particular scene motif; common motifs are intentionally shared where historically and visually appropriate.
- `js/app.js`: three-beat sequence, autoplay schedule, keyboard navigation, deep links, modal notes, and sound cues.

No external libraries are required. Avoid animations that sensationalize child exploitation. The later acts intentionally use restrained archival motion rather than cartoonized depictions of abuse.

## Visual identity

The global color tokens and fonts are at the start of `css/site.css`. The dark museum-gallery background, ivory vector art, and gold/teal labeling are consistent across the full story.

## Test

```bash
python tools/smoke_test.py
```

The test uses Playwright, which is *only* a development-time testing tool. Visitors do not need it. In restricted test environments it creates the same page from inlined project assets rather than navigating to blocked local URLs.

## Add more scenes in the future

If expanding beyond 43 scenes, adjust the totals and act boundaries in `js/app.js`, the hero copy and HTML counters in `index.html`, the expected illustration count in `tools/sync_illustrations.py`, and the test in `tools/smoke_test.py`. Alternatively, refactor these to use `S.length` and a shared acts configuration before adding many scenes.
