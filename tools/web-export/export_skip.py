"""Names the web export leaves out of every tile (people placeholders, task chairs, grass scatter,
GN instancers, cameras, retired and backup objects). Shared by make_chunks.py and by
blender/scripted/adopt.py, which does not adopt what the main tiles never showed."""

import re

EXCL = re.compile(
    r"(grass_points|grass_fill|Lawn_grass|_grass_|cx_grass|GN instances|people placeholders|task chairs|Context_ground_beyond|_CAM_|^CAM_|WALK_\d|RETIRED|_bak_|walk_joints_auto|slab_joints_GN|panel_tone_chips)",
    re.I,
)
