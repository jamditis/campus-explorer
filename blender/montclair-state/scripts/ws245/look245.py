import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
t=bvh(bpy.data.objects['WS243_stands_pitch_holdunder_target']); d=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'])
pads={n:bvh(bpy.data.objects[n]) for n in ['fse_stand_under_pad','fse_front_walkway','fs_turf','fse_stand_entry_steps']}
X0,Y0=float(os.environ.get('LX','-219.7')),float(os.environ.get('LY','120.3'))
dt=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('LK mods',[(m.name,m.type) for m in dt.modifiers],flush=True)
for dy in range(4,-5,-1):
    row=[]
    for dx in range(-4,5):
        p=Vector((X0+dx,Y0+dy,300)); h=t.ray_cast(p,Vector((0,0,-1)),400)[0]; g=d.ray_cast(p,Vector((0,0,-1)),400)[0]
        w=[k[4:10] for k,b in pads.items() if b.ray_cast(p,Vector((0,0,-1)),400)[0] is not None]
        row.append('%s/%s%s'%('%.2f'%h.z if h else '----','%.2f'%g.z if g else '----',(','.join(w))[:6]))
    print('LK y=%.1f '%(Y0+dy),' '.join(row),flush=True)
os._exit(0)
