import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
def bvo(o):
    mw=o.matrix_world; me=o.data
    return BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
fp=ob('Footpaths_OSM'); mw=fp.matrix_world
fs=[(mw@p.center,p) for p in fp.data.polygons]
near=[(c,p) for c,p in fs if -218<=c.x<=-204 and -162<=c.y<=-150]
for c,p in sorted(near,key=lambda t:t[0].y)[:40]:
    vs=[mw@fp.data.vertices[i].co for i in p.vertices]
    print('FP',p.index,round(c.x,2),round(c.y,2),round(c.z,2),fp.data.materials[p.material_index].name,[(round(v.x,2),round(v.y,2)) for v in vs])
t=ob('Terrain_LiDAR_DTM_1m'); tw=t.matrix_world
for p in t.data.polygons:
    c=tw@p.center
    if -216<=c.x<=-205 and -163<=c.y<=-158: print('TR',p.index,round(c.x,2),round(c.y,2),round(c.z,2),t.data.materials[p.material_index].name)
P=bvo(ob('WS120_Chapin_W_N_plaza_ext')); F=bvo(fp); T=bvo(ob('WS102_CollegeAve_S_carriageway')); C=bvo(ob('WS27_CollegeAve_curb_right')); C2=bvo(ob('WS27_CollegeAve_curb_left')); R27=bvo(ob('WS27_CollegeAve_carriageway'))
def z(b,x,y):
    h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else round(h[0].z,3)
for y in (-163,-162.1,-161.5,-160.5,-159.5,-158.5,-157.5):
    print('ROW',y,[(x,z(P,x,y),z(F,x,y),z(T,x,y),z(C,x,y),z(C2,x,y),z(R27,x,y)) for x in range(-216,-203,1)])
pe=ob('WS120_Chapin_W_N_plaza_ext'); pm=pe.matrix_world
vs=[pm@v.co for v in pe.data.vertices]; top=[v for v in vs if v.y>-162.05]
print('PE N edge',sorted([(round(v.x,2),round(v.z,2)) for v in top])[:60])
