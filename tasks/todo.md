# Viewer upgrade: fun, fast, accurate

Plan for the viewer work on branch `joe/wizardly-pasteur-n7mq4j`. Architecture and module contract: [docs/VIEWER.md](../docs/VIEWER.md).

## Fast

- [ ] Stream tiles: show the view after the far-field ground and the nearest tiles, load the rest nearest-first while you explore
- [ ] Decode meshopt geometry in workers; compile shaders before a tile is added
- [ ] Draw only when something changed; redraw shadows only when the sun, the focus or the scene changed
- [ ] Adaptive resolution: drop resolution while moving on a slow GPU, sharpen when still
- [ ] Build collision BVHs on demand near the player instead of for the whole campus when Walk starts
- [ ] Ask before streaming the full campus on a data-saver connection

## Accurate

- [ ] Sun direction fix: the default sun sits in the north-west sky, which cannot happen at 40.86° N. Use a real date and time
- [ ] Time-of-day control with the real solar position for the campus; "now" button
- [ ] Georeference in the viewer: latitude, longitude and NAVD88 elevation readout, compass (true north), scale bar
- [ ] Overview framing from the real tile extents (the hard-coded box has north and south swapped)
- [ ] Measuring tool: distance, horizontal run and height difference between picked points
- [ ] Place names and positions from OpenStreetMap, with the source shown; nothing inferred from joined mesh names
- [ ] Walk collision: slide along walls, step up curbs and stairs, never fall through gaps

## Fun

- [ ] Search and fly to any named building; labels over the model
- [ ] Minimap drawn from the model itself; click to go there
- [ ] Guided tour
- [ ] Landmark hunt in walk mode
- [ ] Touch sticks and gamepad support; smoother fly and walk
- [ ] Share link that restores the exact view; photo button
- [ ] Keyboard shortcuts and a help sheet
- [ ] Lamps glow at night

## Quality

- [ ] Unit tests (`node --test tests/`) for every pure module; run in CI
- [ ] Headless smoke test and standard screenshots that run anywhere (`tools/viewer-test/`)
- [ ] Before/after screenshots of the same views
- [ ] Favicon and social sharing tags
- [ ] Docs: VIEWER.md, README, ROADMAP, AGENTS index
- [ ] Independent review pass before the PR

## Review

(filled in at the end)
