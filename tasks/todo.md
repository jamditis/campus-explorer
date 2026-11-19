# Viewer upgrade: fun, fast, accurate

Plan for the viewer work on branch `joe/wizardly-pasteur-n7mq4j`. Architecture and module contract: [docs/VIEWER.md](../docs/VIEWER.md).

## One campus (added after Joe's correction, 2026-11-18)

- [x] Remove the main / north scene switch from the viewer, links, docs and tools
- [x] `tools/web-export/unify.mjs`: divide the ground between the two Blender files on a 2 m grid, write `models/manifest.json` and `models/ownership.png`
- [x] Viewer draws and collides with each cell from one file only (shader discard, depth materials, `solidAt`)

## Phones and full screen (added on Joe's request, 2026-11-18)

- [x] Full screen button and `F` key; an "immersive" fallback where the browser has no Fullscreen API (iPhone Safari)
- [x] Phone layout: one top bar with search, full screen, controls and the mode switch; portrait and landscape
- [x] Lite profile for phones: nine tiles near the view, eviction, no skirt, lower pixel ratio
- [x] Touch sticks and buttons for fly and walk

## Fast

- [x] Stream tiles: show the view after the far-field ground and the nearest tiles, load the rest nearest-first while you explore
- [x] Decode meshopt geometry in workers; compile shaders before a tile is added
- [x] Draw only when something changed; redraw shadows only when the sun, the focus or the scene changed
- [x] Adaptive resolution: drop resolution while moving on a slow GPU, sharpen when still
- [x] Build collision BVHs on demand near the player instead of for the whole campus when Walk starts
- [x] Ask before streaming the full campus on a data-saver connection

## Accurate

- [x] Sun direction fix: the default sun sits in the north-west sky, which cannot happen at 40.86° N. Use a real date and time
- [x] Time-of-day control with the real solar position for the campus; "now" button
- [x] Georeference in the viewer: latitude, longitude and NAVD88 elevation readout, compass (true north), scale bar
- [x] Overview framing from the real tile extents (the hard-coded box has north and south swapped)
- [x] Measuring tool: distance, horizontal run and height difference between picked points
- [x] Place names and positions from OpenStreetMap, with the source shown; nothing inferred from joined mesh names
- [x] Walk collision: slide along walls, step up curbs and stairs, never fall through gaps

## Fun

- [x] Search and fly to any named building; labels over the model
- [x] Minimap drawn from the model itself; click to go there
- [x] Guided tour
- [x] Landmark hunt in walk mode
- [x] Touch sticks and gamepad support; smoother fly and walk
- [x] Share link that restores the exact view; photo button
- [x] Keyboard shortcuts and a help sheet
- [x] Lamps glow at night

## Quality

- [x] Unit tests (`node --test`) for every pure module; run in CI
- [x] Headless smoke test and standard screenshots that run anywhere (`tools/viewer-test/`)
- [x] Before/after screenshots of the same views
- [x] Favicon and social sharing tags
- [x] Docs: VIEWER.md, README, ROADMAP, AGENTS index
- [x] Independent review pass before the PR

## Review

What was checked, and how:

- Unit tests: 117 pass (`node --test`). They cover the georeference, solar position, tile order, share links, place search, ownership rules and the arithmetic of the compass, labels, measuring tool and hunt.
- Georeference: `viewer/geo.js` agrees with pyproj to 5.5e-9 m. Building positions in both source models agree with OpenStreetMap to 4 m or better, with no systematic shift.
- Headless browser (software WebGL): smoke test of every mode and tool, plus screenshots at 1280x800, 390x844 (portrait, touch) and 844x390 (landscape, touch). No overlapping controls, no console errors.
- An independent review of the viewer core found 15 defects; all are fixed (commit 77d2500).
- Before/after screenshots of the seven standard views (`tools/viewer-test/shoot.mjs`).

Not verified (UNVERIFIED):

- The border between the two source models. The 2 m ownership grid and its two patches (University Hall, softball stadium) are a viewer-side rule, not a merge. Sprague Field is drawn half from each file. The real merge belongs in Blender.
- Phone memory and frame rate. The nine-tile lite budget is an estimate; it was tested only in an emulated phone viewport, not on a device.
- `tools/web-export/export_web.py`: the "aerial-draped ground is grass" rule was not run, because Blender is not installed here. The viewer applies the same rule by material name until the next export.
- Frame rates. This machine draws with software WebGL, so no real GPU timing exists.
- Reduced-motion behaviour of the tour and labels (coded, not exercised in a browser).

Lessons are in [lessons.md](lessons.md).
