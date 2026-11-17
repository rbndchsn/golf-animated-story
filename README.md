# The Game Beneath the Game?

**A GitHub Pages-ready motion comic about golf, historical language, symbolic interpretation, and a difficult archival question.**

The exhibit features **43 illustrated scenes in five acts**. Quinn (the Questioner) and Vale (the Archivist) conduct an animated clubhouse conversation. Each scene has three beats: question, response, and a kinetic evidence or interpretation card. Historical reports and allegations are deliberately labeled separately.

## Start here

**Just watch:** Double-click `dist/Golf_The_Game_Beneath_The_Game_Standalone.html`. It includes the entire site as one file and needs no server or internet connection.

**Work on the website:** Open `index.html` in a browser, or run `python -m http.server 8000` in this directory and visit `http://localhost:8000`. There is **no build step** and no required package installation.

**Publish later:** Follow [`docs/DEPLOY_GITHUB_PAGES.md`](docs/DEPLOY_GITHUB_PAGES.md). Upload the **contents** of this folder to your GitHub repository, not the ZIP itself. The GitHub Pages address will automatically load `index.html`.

## What is inside?

```text
golf-animated-story/
├── index.html                         # Public site entry point
├── .nojekyll                           # GitHub Pages compatibility
├── README.md
├── assets/
│   ├── illustrations/                  # 43 editable, separate SVG scene illustrations
│   ├── icons/favicon.svg
│   └── social/cover.png                 # Social-preview image
├── css/
│   ├── site.css                        # Visual design and responsive layout
│   └── animations.css                  # Motion choreography
├── data/
│   ├── scenes.js                       # Dialogue, claims, research notes, sources
│   └── illustrations.js                # Offline-readable cache of scene SVG art
├── js/
│   ├── motion.js                        # Kinetic SVG clue animations
│   └── app.js                           # Playback, UI, navigation, accessibility
├── dist/
│   └── Golf_The_Game_Beneath_The_Game_Standalone.html
├── docs/
│   ├── ORIGINAL_STORYBOARD.md
│   ├── DEPLOY_GITHUB_PAGES.md
│   ├── EDITING_THE_STORY.md
│   ├── RESEARCH_AND_EVIDENCE.md
│   └── QA_REPORT.json
└── tools/
    ├── sync_illustrations.py           # Sync edited SVGs to offline art cache
    ├── build_standalone.py             # Rebuild self-contained HTML
    └── smoke_test.py                   # Test navigation in Chromium/Playwright
```

## Player controls

The scene player works with mouse, keyboard, touch, and on narrow screens:

| Action | Control |
|---|---|
| Advance one beat | Space, Right Arrow, or **Hear the Response / Reveal the Clue / Next Scene** |
| Previous scene | Left Arrow or the back button |
| Browse any of 43 scenes | **SCENES** or `I` |
| Navigate by act | Five-section timeline |
| Automatic pacing | **AUTO** (click again to pause) |
| Pacing options | Speed control (0.75×, 1×, 1.25×, 1.5×) |
| Audio cues | **♫** toggles optional subtle synthesized sound effects; off by default |
| Fullscreen | Fullscreen button or `F` |
| Inspect documents | **SOURCE & CONTEXT** when a clue is revealed |
| Share a scene | **SHARE THIS FRAME**, which copies a `#scene=N` link |

The story respects **reduced-motion preferences** and stops its autoplay timer when the browser tab is hidden. There are no external scripts, web fonts, cookies, trackers, or analytics.

## Edit the narrative

Update the content in `data/scenes.js`. Every scene has `quinn`, `vale`, `clue`, `detail`, `status`, and `sourceUrl` fields. Use `FACT`, `LENS`, `MIX`, or `OPEN` accurately. The visible evidence card changes its wording according to the chosen classification.

If you edit the SVG art in `assets/illustrations/`, synchronize the offline cache:

```bash
python tools/sync_illustrations.py
```

Then rebuild the stand-alone file:

```bash
python tools/build_standalone.py
```

More instructions: [`docs/EDITING_THE_STORY.md`](docs/EDITING_THE_STORY.md).

## Historical and editorial boundaries

The story preserves the entire provocative fertility-ritual interpretation and asks whether historic child-caddie arrangements might have enabled sexual exploitation or trafficking. These are **questions and hypotheses**, not findings of organized abuse. Later proven individual cases do not establish an original, systemic or Masonic criminal purpose. Some nineteenth-century claims remain unverified archival leads. The work differentiates testimony, research, symbolism, and allegations throughout. See [`docs/RESEARCH_AND_EVIDENCE.md`](docs/RESEARCH_AND_EVIDENCE.md).

The private working dossier is **not included** in the deployable site, and its private Google Drive URL has intentionally been omitted. If you later wish to publish the original research document, do so as a separate, conscious publishing decision.

## Project status

- Static, dependency-free, single repository
- 43 scenes, 43 SVG files, responsive layout
- Five-act index and deep linking
- Animated speech avatars, hand-drawn scene entrances, bespoke animated clue motifs
- Offline standalone edition
- Browser-tested scene navigation and mobile layout (see `docs/QA_REPORT.json`)
- **Not uploaded to a public GitHub repository and not yet published online.**

