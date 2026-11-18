import bpy, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
args=sys.argv[sys.argv.index('--')+1:]
import bmesh
from mathutils.bvhtree import BVHTree
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
TT=[bvh(n) for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')]
def gz(x,y): return max([t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0].z for t in TT if t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] is not None]+[0])
L,T_,lens,eye,th=eval(args[0])
loc=Vector((L[0],L[1],gz(L[0],L[1])+eye)); tgt=Vector((T_[0],T_[1],gz(T_[0],T_[1])+th))
cam=bpy.data.objects.new('probecam',bpy.data.cameras.new('probecam')); sc.collection.objects.link(cam)
cam.location=loc; cam.data.lens=lens; cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); bpy.context.view_layer.update(); W,H=768,432
sc.render.resolution_x=1280; sc.render.resolution_y=720
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
for pxy in args[1:]:
    px,py=map(float,pxy.split(','))
    u=px/W; v=1-py/H
    # frame corners: fr[0]=top-right, fr[1]=bottom-right, fr[2]=bottom-left, fr[3]=top-left
    tl,tr,bl=fr[3],fr[0],fr[2]
    p=tl+(tr-tl)*u+(bl-tl)*(1-v)
    o=mw.translation; d=(mw@p-o).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,o,d)
    print('PROBE152',pxy,ob.name if ob else None,tuple(round(c,2) for c in loc) if hit else None, 'mat', (ob.material_slots[ob.data.polygons[idx].material_index].name if ob and ob.type=='MESH' and ob.material_slots and idx<len(ob.data.polygons) else '-') if hit else '')
