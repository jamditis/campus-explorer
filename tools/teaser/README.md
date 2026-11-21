# Teaser film

A short film of the Montclair State model, shot frame by frame in the project's own browser viewer
(headless Chromium, software WebGL), with its titles and measures as real 3D objects in the scene.
The frames, the film and the fonts' outlines are renders: they are written only to the output folder
you name, never inside the repository.

```sh
# 1. capture (hours: one software draw of the whole campus takes 20 to 45 s); resumable, run it again
#    after a stop and it carries on from the last frame on disk. --step 12 first gives an animatic.
PYTHONPATH=<folder with fontTools> node tools/teaser/capture.mjs /tmp/teaser [--step 12] [--only travel]
# 2. grade, letterbox, grain and encode: /tmp/teaser/teaser.mp4 (H.264, faststart, no sound)
python3 tools/teaser/finish.py /tmp/teaser --fps 24
# 3. sound (tools/teaser/sound/README.md)
node tools/teaser/sound/timeline.mjs > /tmp/tl.json
python3 tools/teaser/sound/mix.py SRC_DIR /tmp/teaser/sound --timeline /tmp/tl.json --video /tmp/teaser/teaser.mp4
```

fontTools is needed once, to turn the machine's Inter Display into letter outlines
(`pip install --target <folder> fonttools`; the capture runs `font.py` and keeps the result in
`<out>/fonts/`).

| File | What it does |
|---|---|
| `storyboard.mjs` | Shots (camera keys, lens, light, speed), the 3D graphics, the grade per sequence, the sound's hit points, and the facts shown on screen with their sources |
| `path.mjs` | Pure maths: splines walked by length, eased speed, the frame clock, graphics timing, dimension lines, type layout (tested in `tests/teaser.test.mjs`) |
| `page.mjs` | In the page: poses a frame, draws it once when the viewer has gone quiet, holds a shadow box per shot |
| `graphics.mjs` | In the page: extruded letters, dimension lines and pins added to the viewer's scene, lit and shadowed by its sun |
| `capture.mjs` | Opens the viewer once, films every frame of the storyboard, restarts the tab if it crashes |
| `font.py` | Letter outlines (curves flattened, holes sorted) from a font file |
| `blend.py` | Averages sub-frames for motion blur (`--sub N` on shots marked `blur`) |
| `finish.py` | The film finish on the rendered pixels (grade, 2.39:1 letterbox easing, vignette, bloom, grain) and the encode |

Nothing here changes the viewer: the capture reaches it only through `window.__campus` (the `?capture`
test hook in `app.js`).
