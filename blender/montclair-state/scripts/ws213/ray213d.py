import bpy, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
BB=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
X0,X1,Y0,Y1=-270,-245,-70,-48
want=[n for n,v in BB.items() if v[0]=='MESH' and not v[1] and not (v[3]<X0 or v[2]>X1 or v[5]<Y0 or v[4]>Y1) and not n.startswith(('Context_skirt','BD_farfield'))]
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in want if n in a.objects]
T=[]
for o in b.objects:
    if o is None or o.type!='MESH' or len(o.data.polygons)==0 or o.hide_render: continue
    m=o.matrix_world; T.append((o,BVHTree.FromPolygons([m@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])))
cam=Vector((-259.0,-53.5,126.6)); tgt=Vector((-255.5,-58.5,124.9))
q=(tgt-cam).to_track_quat('-Z','Y'); fw=q@Vector((0,0,-1)); rt=q@Vector((1,0,0)); up=q@Vector((0,1,0))
W,H=640,360; f=30/36*W
for (px,py,lab) in [(140,215,'wedge L of curb end'),(250,207,'berm foot'),(330,215,'crease'),(200,210,'under curb end'),(360,195,'berm tip right'),(100,240,'asphalt L')]:
    d=(fw*f+rt*(px-W/2)-up*(py-H/2)).normalized(); hits=[]
    for o,t in T:
        h=t.ray_cast(cam,d,200)
        if h[0] is not None: hits.append((round(h[3],2),o.name,o.data.materials[o.data.polygons[h[2]].material_index].name if o.data.materials else None,tuple(round(x,2) for x in h[0])))
    hits.sort(); print('RAY',lab,hits[:4],flush=True)
