# ws267 (merge208 CHAIN, on main ws266b): police south terrace bed lawn (UNIFY police south-walk strip).
# The sunken bed inside the white terrace walls S of the police building (x -353..-339, y -18..-11) rendered as a flat
# grey-green slab with no blades. The NJ 2020 ortho shows it as uniform mown green (lawn); grass type UNVERIFIED (no close photo).
# Points precomputed outside Blender (bed267a_points.json, from probe267a base-mesh samples): 64 pts/m2 like the police lawn,
# 0.15 m off the terrace walls with the ws266 trimmed-edge easing, z = IDW of 4 nearest bed samples - 1 cm. Appended to
# gd_grass_police_lawn_points (same blade look as the lawn N of the walk).
import bpy, json
from mathutils import Vector
TAG='F267A'; D='/workspace/nj-scenes/montclair-state/'
G=bpy.data.objects['gd_grass_police_lawn_points']; me=G.data; Wi=G.matrix_world.inverted()
if me.get('ws267a_bed'): raise SystemExit('F267A already applied')
B=bpy.data.objects['ge_police_terrace_bed']
print(TAG,'bed mods',[(m.name,m.type) for m in B.modifiers],'mats',[s.material and s.material.name for s in B.material_slots],flush=True)
P=json.load(open(D+'scripts/ws267/bed267a_points.json')); n0=len(me.vertices)
me.vertices.add(len(P))
for v,p in zip(me.vertices[n0:],P): v.co=Wi@Vector(p)
me.update(); me['ws267a_bed']=len(P)
print(TAG,'grass points',n0,'->',len(me.vertices),flush=True)
