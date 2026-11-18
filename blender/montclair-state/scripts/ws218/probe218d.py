import bpy, json, re
from mathutils import Vector
S='/workspace/nj-scenes/montclair-state/scripts/'
BB=json.load(open(S+'ws205/bbox205.json'))
cx0,cx1,cy0,cy1=-200,-110,195,250
want=[n for n,v in BB.items() if v[0]=='MESH' and not v[1] and not n.startswith('BD_farfield') and not (v[3]<cx0 or v[2]>cx1 or v[5]<cy0 or v[4]>cy1) and (v[3]-v[2])<5000]
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state_ws218a.blend') as (a,b): b.objects=[n for n in want if n in set(a.objects)]
TRX=re.compile(r'band_to_DTM|terrain|_cut|clamp|LiDAR_patch|regrid|seam_ramp|edge_grade|hump',re.I)
sc=bpy.context.scene
for o in b.objects:
    sc.collection.objects.link(o)
    for m in o.modifiers:
        if m.type=='NODES' and TRX.search(m.name) and 'skirt' not in m.name.lower(): continue
        m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get()
for px,py in [(-160,210),(-160,216),(-160,219),(-159,222),(-140,215),(-180,215),(-125,215),(-130,205),(-195,230),(-110,260)]:
    hits=[]; z=300
    for _ in range(4):
        r=sc.ray_cast(dg,Vector((px,py,z)),Vector((0,0,-1)))
        if not r[0]: break
        hits.append((r[4].name[:45],round(r[1].z,2))); z=r[1].z-0.01
    print('P218D',px,py,hits,flush=True)
