# Lessons

Rules learned from corrections. Read at the start of a session.

## 2026-11-18: one campus, one scene

- **Correction (Joe, during the viewer upgrade):** "the goal is to have a single unified scene with all buildings and textures and everything in one scene, not multiple scenes."
- **What went wrong:** the viewer work kept the main / north scene switch and built new features (permalinks, places, tests) around a `scene` setting.
- **Rule:** the campus is one scene everywhere: viewer, links, docs, tools. Do not add or keep a scene switch. New exports must end up in `models/manifest.json` through `tools/web-export/unify.mjs`.
- **How it is done for now:** the two Blender files overlap and each holds objects the other lacks. Joined tiles cannot be merged object by object, so `unify.mjs` divides the ground between the files and the viewer draws each cell from one file. The real merge belongs in Blender; the borders stay UNVERIFIED until then.
- **Method that worked:** a software top-down render of the tiles (`unify.mjs --preview`) showed what each file covers in seconds, when WebGL renders on this machine took many minutes.

## 2026-11-18: mesh names in the tiles are not object names

- The exporter joins meshes by material. A node called "Morehead Hall walls" spans several buildings.
- **Rule:** never show a tile's node name as the identity of what the user clicked. Names in the viewer come from a cited source (OpenStreetMap today).

## 2026-11-18: check compass directions against the axes

- The old default sun used a spherical angle that put it in the north-west sky, which cannot happen at 40.86° N. Viewer space has grid north on **-Z**.
- **Rule:** derive directions from `viewer/geo.js` and `viewer/sun.js`, and test them, instead of typing angles by hand.

## 2026-11-19: short probes beat a long browser test on a machine without a GPU

- **Question (Joe, while a smoke run was in progress):** "do we really need a smoke test"
- **What went wrong:** three full smoke runs of 20 minutes each failed on the test's own fixed waits, not on the viewer. A second browser in parallel also ran the container out of memory.
- **Rule (my reading of the question, not Joe's words):** where WebGL runs in software, check one behaviour with one short probe script (one or two tiles, a few minutes) and run one browser at a time. Keep the full smoke test for a machine with a GPU. Browser tests wait for a condition, never for a fixed time.
