# ws278 runbook (Sat Nov 28, 2026, ~3:35 → ~3:50 PM ET) — daily model release model-20261128

Session by lgn-cemain (fleet worker on Legion WSL) while Void is out of weekly usage. Main: ws277b (sha256 118867a5…de03).

1. Pre-release check (`run278.sh` step 1: ws267/m5wrap267.py in the merge208 loader, no save):
   - libs [], 0 paths outside, 0 absolute, 0 missing, 0 unresolved, 180 packed images.
   - Known items, as in ws267: 1 NaN helper (WS113_paving_tops_proxy), 3 empty GN carriers.
   - 10,513 objects (10,182 in the scene).
2. Release (`strip278.sh` = ws268/strip268.sh with the date changed, GATE=3300):
   - Output: /workspace/nj-scenes/exports/model-20261128/montclair_state_20261128.blend, 336,260,288 B.
   - ver244_lowmem: VER libs [] / unpacked []. sha256 1739cd01…9fcf.
3. Published: `gh release create model-20261128 -R jamditis/campus-explorer --title "Montclair State model 2026-11-28"
   --notes-file NOTES.md montclair_state_20261128.blend SHA256SUMS.txt`. GitHub asset digest = local sha256. Staging .blend
   removed.
4. Tiles: not a full main re-export. Published main tiles stay from ws251b except t_-1_0 (ws276b, #160) and t_-3_-2 (ws277b,
   #166). A full re-export from this release-derived file needs:
   - the ws211…ws221 paint mask tile lists (they live on Void's box);
   - a colour check of every tile against the published one (ws276/colcmp276.mjs). The release strip's stand-in RGBs replace
     ortho averages; see ws276 RUNBOOK 3b.
   Void's own working file still has the ortho images and does not have this problem.
