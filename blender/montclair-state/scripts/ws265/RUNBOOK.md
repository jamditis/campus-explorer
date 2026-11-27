# ws265 runbook (Fri Nov 27, 2026, 2:38 → ~3:30 PM ET) — W69 police flat lawn: grass fill to the existing core density

Main before: ws264c (sha ec502c3a…). Backup montclair_state_pre_20261127ws265.blend = ws264c. Chain via `run265.sh`
(= ws264/run264.sh with F265/P265/C265 tags; ws208/merge208.py, base meshes): ws264c + `f265a.py` → ws265a; + `f265b.py` → ws265b = MAIN.

1. `probe265a.py` (merge208 CHAIN, no save; modifiers re-enabled only on meshes meeting the W263 mask box x −354.68…−323.43,
   y −7.61…35.64): 11,160 jittered 0.35 m ray samples on the evaluated scene → eval265a.json (x, y, top, z, normal z, ortho RGB
   at the hit via the hit face's UV). Tops: WS68_RHD_ground_northDTM 5,893, M3b west-rail-corridor DTM 1,953, police roof/outbuilding,
   Red Hawk Deck top. Top-down plots (renders/test/ws265_police_*_topdown.png): the merged north grass is an L (N band + strip along
   the deck); the W-centre of WS68 and the M3b strip W of it had no blades but the same ortho tone as under the grass.
2. `f265a.py`: existing-point density on a 0.5 m grid (blur sigma 1 m), core = p60 = 64 pts/m². New points fill the deficit only where
   the nearest sample is WS68/M3b ground with normal z > 0.5 and ortho luminance < 0.55 (drops the pale band along the deck face),
   ≥ 0.5 m from any non-ground top; fade over 3 m toward the box edge and 1 m toward non-ground. Each point ray-snapped to the
   evaluated top − 1 cm (0 dropped). 21,536 points appended to gd_grass_police_lawn_points (24,501 → 46,037; the mesh has no extra
   point attributes). The W263 soil mask is rebuilt from all points with the same box/grid (125 × 173, 0.25 m) as
   //data/ws265/police_grass_density265.png and both W263_mask nodes point at it (the ws263 png is left on disk for the backups).
   Peak memory 4.0 GB (evaluated modifiers in the box).
3. `m5check264.py` rerun on ws265a (m5check264_ws265a.out).
4. WIPs `jobwip265.sh` (subrend234, terrain GN on, crop259, EXTRAJ ws262/extra262p.json + KEEPMOD grass points): oblique from SW
   high, eye from W (same camera as ws264), eye from S across the fill, close-up of blades over the soil layer.
5. Self-review of the ws265a WIPs (eye from S, close-up): bald grey patches inside the fill = samples rejected by the 0.55 luminance
   cut (ortho 0.55–0.85 = sun-bleached lawn spots, ~10% of the W-centre). `f265b.py` = second pass with the cut at 0.85 (the white
   band along the deck face is > 0.9), deficit against all 46,037 points: 4,980 points. First try snapped on the evaluated ground and
   was killed by the MemAvailable watchdog at 1.16 GB (host memory balloon back at ~3.3 GB available; nothing saved). Retry snaps
   z = inverse-distance mean of the 4 nearest probe265a ground samples − 2 cm (no modifier evaluation; peak 1.9 GB) →
   ws265b (51,017 points; mask rebuilt as //data/ws265/police_grass_density265b.png) = MAIN.
