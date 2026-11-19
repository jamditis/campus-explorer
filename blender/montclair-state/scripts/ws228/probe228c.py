import bpy,bmesh,sys,os
from mathutils import Vector
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bm=bmesh.new(); bm.from_mesh(t.data)
for P in [(246.29,-248.74),(245.97,-33.5)]:
    V=[v for v in bm.verts if (v.co.to_2d()-Vector(P)).length<0.05][0]
    fs=list(V.link_faces)
    print('P228C apex',P,'nf',len(fs),flush=True)
    for f in sorted(fs,key=lambda f:-f.calc_area())[:12]:
        c=f.calc_center_median(); print('P228C  f area',round(f.calc_area(),1),'nv',len(f.verts),'c',round(c.x,1),round(c.y,1),'far',max(round((v.co.to_2d()-Vector(P)).length) for v in f.verts),flush=True)
sys.stdout.flush(); os._exit(0)
