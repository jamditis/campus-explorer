import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('WS107_Chapin'):
        mw=o.matrix_world; vs=[mw@v.co for v in o.data.vertices]; nr=[v for v in vs if -217<=v.x<=-213 and -204<=v.y<=-199]
        if nr: print('W107',o.name[:60],len(nr),round(min(v.z for v in nr),3),sorted(set((round(v.x,2),round(v.y,2)) for v in nr))[:12])
for o in bpy.data.objects:
    if o.type!='MESH': continue
    mw=o.matrix_world
    if len(o.data.vertices)>300000: continue
    hit=[mw@v.co for v in o.data.vertices if -216.2<=(mw@v.co).x<=-214.8 and -201.9<=(mw@v.co).y<=-200.9]
    if hit and not o.name.startswith('T_'): print('NEAR',o.name[:70],len(hit),round(min(v.z for v in hit),3),round(max(v.z for v in hit),3))
dg=bpy.context.evaluated_depsgraph_get()
fp=bpy.data.objects['Footpaths_OSM'].evaluated_get(dg); me=fp.to_mesh(); mw=fp.matrix_world
b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
for x in (-210.6,-209.8,-209,-208.2,-207.5):
    for y in (-159.65,-159.3):
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); print('FPE',x,y,None if h[0] is None else round(h[0].z,3))
