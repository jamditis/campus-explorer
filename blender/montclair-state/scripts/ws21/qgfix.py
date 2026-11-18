# ws21: QG north-strip patch deleted terrain faces whose centre hit the patch; where the patch has gaps this left 1-cell holes to the void (dark 'broken paving' cracks north of Life Hall).
# Instead keep the terrain under the patch, dropped 6 cm, as a backing skin.
import bpy,os
ng=bpy.data.node_groups['QG_north_strip_LiDAR_patch_GN']
N=ng.nodes; L=ng.links
dl=N['Delete Geometry']; rc=N['Raycast']; gi=N['Group Input']; jn=N['Join Geometry']
sp=N.new('GeometryNodeSetPosition'); sp.name='WS21_drop_under_patch'; sp.location=dl.location
sp.inputs['Offset'].default_value=(0,0,-0.06)
L.new(gi.outputs['Geometry'],sp.inputs['Geometry'])
L.new(rc.outputs['Is Hit'],sp.inputs['Selection'])
for l in list(L):
    if l.from_node==dl: L.remove(l)
L.new(sp.outputs['Geometry'],jn.inputs['Geometry'])
dl.mute=True
ng['ws21']='delete replaced by 6 cm drop (backing skin under patch)'
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
oe=o.evaluated_get(dg); me=oe.to_mesh(); M=o.matrix_world
print('EVAL faces',len(me.polygons))
T=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
def cnt(T):
    a=b=0
    for x in range(-60,120):
        for y in range(60,200):
            loc,n,i,d=T.ray_cast(Vector((x+.5,y+.5,200)),Vector((0,0,-1)))
            if loc is None:
                a+=1
                if -5<=x<60 and 95<=y<130: b+=1
    return a,b
print('MISS wide/court',cnt(T))
oe.to_mesh_clear()
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
