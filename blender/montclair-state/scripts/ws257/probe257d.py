# ws257 read-only: (1) Red Hawk Deck pieces in main near the Maintenance massing's NE corner (x > -336, y > -47): footprint overlap?
# (2) cells where main ground stands ABOVE the massing roof (would bury it)
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=[n for n in a.objects if n.startswith('MSU Maintenance Building')]
mb=b.objects[0]
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b):
    names=[n for n in a.objects if ('rhd' in n.lower() or 'red hawk' in n.lower())]
    b.objects=names+['WS68_RHD_ground_northDTM (north grid_1m dtm_filled; NJ 2020 ortho)'] if 'WS68_RHD_ground_northDTM (north grid_1m dtm_filled; NJ 2020 ortho)' in a.objects else names
print('P257D rhd-named objects in main',len(names))
M=mb.matrix_world; mv=np.array([M@v.co for v in mb.data.vertices])
fp=BVHTree.FromPolygons([Vector(v) for v in mv],[p.vertices[:] for p in mb.data.polygons])
def hits(bt,x,y):
    out=[]; o=Vector((x,y,400))
    while True:
        h=bt.ray_cast(o,Vector((0,0,-1)),600)
        if not h[0]: return out
        out.append(h[0].z); o=Vector((x,y,h[0].z-0.001))
ov={}
for o in b.objects:
    if not o or o.type!='MESH': continue
    W=o.matrix_world; vs=[W@v.co for v in o.data.vertices]
    ps=[p.vertices[:] for p in o.data.polygons if any(vs[i].x<-320 and vs[i].y<-34 for i in p.vertices)]
    if not ps: continue
    bt=BVHTree.FromPolygons(vs,ps); k=0; above=0
    for x in np.arange(-340,-322,0.25):
        for y in np.arange(-50,-36,0.25):
            hm=hits(fp,x,y)
            if len(hm)<2: continue
            hz=hits(bt,x,y)
            if any(min(hm)+0.3<z<max(hm)-0.05 for z in hz): k+=1
    if 'WS68' in o.name:
        for x in np.arange(-393,-323,1.0):
            for y in np.arange(-79,-36,1.0):
                hm=hits(fp,x,y)
                if len(hm)<2: continue
                hz=hits(bt,x,y)
                if hz and max(hz)>max(hm)+0.05: above+=1
    print('P257D',o.name[:50],'faces near corner',len(ps),'cells inside massing',k,('ground above roof cells %d'%above) if 'WS68' in o.name else '')
os._exit(0)
