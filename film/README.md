# Full film: The Game Beneath the Game?

The original film in `export/The_Game_Beneath_The_Game_Full_Film.mp4` contains all 43 scenes and their spoken lines and visual evidence reveals, arranged as one 12m43s 720p video. This is a single-file, independent film that can be viewed outside the website.

**Captions:** `captions.vtt` (WebVTT). **Chapters:** `chapters.json` and `chapters.vtt`. **Preview:** `poster.jpg`.

## Creation and reproducibility

The original vector art and source dialogue are in `assets/illustrations/*.svg` and `data/scenes.js`. The reproducible video generation script is `tools/produce_film.py`. It requires FFmpeg, its bundled Flite speech source, Python, Pillow, CairoSVG, NumPy, and SoundFile. It creates stills, voice tracks, a synchronized audio soundtrack, and the video. These intermediate build outputs are not part of the public repository.

### Speech and soundtrack

The **offline synthetic narration** uses different Flite voices for the Questioner (Quinn), the Archivist (Vale), and the clue/act narration. It is not a live human recording or a high-end neural TTS model. The subdued harmonic background is an original generated ambient score with no licensed music.

### Editorial standards

The presentation retains the interpretive and historical claims as labeled in the 43-scene script. Historical child caddying is documented; claims of an intentional fertility ritual or a nineteenth-century organized trafficking institution are hypotheses, **not established historical conclusions**. The children are illustrated exclusively as workers in historical contexts, without sexualization.

## GitHub Pages video delivery

The public site contains `chunks/film_00.part`, etc., and a checksum/size manifest rather than a single >9 MB Git blob. `js/film.js` fetches the binary chunks in parallel and reconstructs the *exact* original MP4 in memory as one Blob URL, so the browser provides a normal full-duration video timeline and seekers can jump across chapters. Download MP4 saves that complete reconstructed file. This is a transport/build constraint, not a split user experience. The original unchunked MP4 is retained in the Drive project and outside the website build.
