import bpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
EX0,EX1,EY0,EY1=182,258,292,320
POLY=[(50,320),(EX0,320),(EX0,EY0),(EX1,EY0),(EX1,320),(300,320),(300,509),(50,509)]
def dseg(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;t=((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy);t=min(max(t,0),1);return math.hypot(px-ax-t*dx,py-ay-t*dy)
def dpoly(x,y): return min(dseg(x,y,POLY[i],POLY[(i+1)%8]) for i in range(8))
def ss(t): t=min(max(t,0),1); return t*t*(3-2*t)
for n in ('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WJ_south_gully_LiDAR_patch_ext_UNVERIFIED'):
    o=bpy.data.objects[n]; me=o.data
    a=me.attributes.get('wj_in') or me.attributes.new('wj_in','FLOAT','POINT')
    for i,v in enumerate(me.vertices):
        c=o.matrix_world@v.co; a.data[i].value=ss(dpoly(c.x,c.y)/4.0)
ng=bpy.data.node_groups['WJ_skirt_under_south_gully']; N=ng.nodes; K=ng.links
rc=[n for n in N if n.type=='RAYCAST'][0]; rc.data_type='FLOAT'
na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT'; na.inputs['Name'].default_value='wj_in'
K.new(na.outputs['Attribute'], rc.inputs['Attribute'])
sub=[n for n in N if n.type=='MATH' and n.operation=='SUBTRACT' and not n.inputs[1].is_linked and abs(n.inputs[1].default_value-0.30)<1e-6][0]
ma=N.new('ShaderNodeMath'); ma.operation='MULTIPLY_ADD'
K.new(rc.outputs['Attribute'], ma.inputs[0]); ma.inputs[1].default_value=0.28; ma.inputs[2].default_value=0.02
K.new(ma.outputs[0], sub.inputs[1]); print('DIP linked 0.02+0.28*wj_in')
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
bw=bvh('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED');be=bvh('WJ_south_gully_LiDAR_patch_ext_UNVERIFIED');bs=bvh('Context_skirt_3DEP_ortho_4km')
cnt=0;mx=0;lip=[]
for y in np.arange(292.25,336,0.5):
    for x in np.arange(182.25,258,0.5):
        ps=[h[0].z for h in (bw.ray_cast(Vector((x,y,400)),Vector((0,0,-1))),be.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))) if h[0] is not None]
        s=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        if ps and s is not None and s.z>max(ps)+0.03: cnt+=1; mx=max(mx,s.z-max(ps))
# lip just outside east/south/west edges
for y in np.arange(293,320,1.0):
    for x in (EX1+0.3,):
        s=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; e=be.ray_cast(Vector((EX1-0.01,y,400)),Vector((0,0,-1)))[0]
        if s and e: lip.append(e.z-s.z)
print('RESID',cnt,round(mx,2),'EASTLIP max',round(max(lip),3),'mean',round(sum(lip)/len(lip),3))
bpy.ops.wm.save_mainfile()
