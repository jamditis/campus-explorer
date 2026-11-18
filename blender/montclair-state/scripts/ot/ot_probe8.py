import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    me=o.data; mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
bt=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m']); bs=bvh(bpy.data.objects['Context_skirt_3DEP_ortho_4km'])
def z(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return round(h[0].z,1) if h[0] else None
print('N',[(x,z(bt,x,246),z(bs,x,252)) for x in range(-240,241,40)])
print('S',[(x,z(bt,x,-247),z(bs,x,-253)) for x in range(-240,241,40)])
print('W',[(y,z(bt,-247,y),z(bs,-253,y)) for y in range(-240,241,40)])
print('E',[(y,z(bt,244,y),z(bs,250,y)) for y in range(-240,241,40)])
# where is the skirt hole edge? along x=0 find first y with skirt hit going north from 0
print('HOLE', [(y,z(bs,0,y)) for y in range(150,260,10)], [(x,z(bs,x,0)) for x in range(150,260,10)], [(x,z(bs,x,0)) for x in range(-260,-150,10)],[(y,z(bs,0,y)) for y in range(-260,-150,10)])
