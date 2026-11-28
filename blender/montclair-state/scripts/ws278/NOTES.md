Daily model release for Nov 28, 2026: Montclair State University campus (Blender 4.5, single .blend).

- Source: main scene after session ws277 (ws277b, saved 3:33 PM ET Nov 28; main sha256 118867a527a2a3817ef7fe3bb9608e75621cf41977439ccf43cf20805ba9de03), published by session ws278. Sessions ws275–ws278 were run by the fleet worker lgn-cemain while Void is away; each has a RUNBOOK under blender/montclair-state/scripts/.
- Asset: montclair_state_20261128.blend, 336,260,288 bytes, compressed, all libraries made local and packed.
- Asset sha256: 1739cd01059c3ed2ff458514fc065806f0c8434b1b55f8785ac7e102d1209fcf (also in SHA256SUMS.txt).
- Stripped: aerial/ortho imagery, NAIP tiles and LiDAR-derived ground rasters. The source was built on model-20261127, which had none left, so no images were removed this time. CC0 and own textures are kept.
- Verified: opens in Blender 4.5 with no linked libraries and no unpacked images.
- Pre-release check on the source found 0 absolute paths, 0 missing files and 0 unresolved libraries. Known items: 1 NaN helper, 3 empty GN carriers.

Changes since model-20261127 (sessions ws268–ws277):
- College Ave / Lot 33 (ws268–ws270, ws274):
  - Paving lifted onto the ground with an edge shoulder.
  - Stall paint and a tree island with its tree (species UNVERIFIED).
  - North curb and gutter along the police lawn, with a curb cut at the police south walk (UNVERIFIED).
  - Westbound turn arrow and a faded yellow hatch painted into the asphalt (arrow type and colour UNVERIFIED).
- Sprague grandstand lawn:
  - Seam step closed (ws271).
  - The fill ridge against the Panzer gym north wall replaced by a smooth harmonic fill (ws272, shape UNVERIFIED).
  - One lawn over the grandstand lawn and lot pocket, replacing old roof-coloured ortho (ws273).
- Rule 16 audit (ws275): no housing interiors in the main file; nothing removed.
- Sprague Library east doorway (ws276): a 2.0 × 2.4 m opening for the rough interiors, with brick reveals. The Sprague roof gets its pre-release tone back.
- Alumni House (ws277): LiDAR context massing on its OSM outline south of Normal Ave W. Eave, wing height and wall colour are UNVERIFIED.
- Still rough:
  - The north source file is unchanged since model-20261127 and was not re-checked for rule 16.
  - The ground west of the TV Tower block is still the coarse far terrain (no visible seam).
  - A small untextured sliver above the Sprague doorway.
