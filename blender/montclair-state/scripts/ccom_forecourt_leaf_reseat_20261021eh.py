# Session eh: the eh lawn ramp raised the DTM up to 0.2 m around the CCOM west forecourt, burying faces of
# 'Fallen_leaves_under_maples (3f)' (leaf litter vanished in the closeF WIP). Re-seat leaf faces within 4 m of the forecourt
# that now sit below the terrain to terrain + 1 cm (skip faces over the paving). Pre-change z in point attr eh_orig_z.
# SAVE=1 saves; REVERT=1 restores.
import bpy, bmesh, mathutils, os
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
lf=bpy.data.objects['Fallen_leaves_under_maples (3f)']; me=lf.data; mw=lf.matrix_world; inv=mw.inverted()
at=me.attributes.get('eh_orig_z')
if REV:
    if at:
        for v,d in zip(me.vertices,at.data):
            if d.value>-9000: v.co.z=d.value
        me.attributes.remove(at); me.update()
    print('EH_LEAF_REVERT')
else:
    fc=bpy.data.objects['CCOM brick forecourt (ortho + photo)']; fb=bmesh.new(); fb.from_mesh(fc.data); fb.transform(fc.matrix_world); fv=BVHTree.FromBMesh(fb)
    xs=[v.co.x for v in fb.verts]; ys=[v.co.y for v in fb.verts]
    ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tb=bmesh.new(); tb.from_mesh(ter.data); tb.transform(ter.matrix_world); tv=BVHTree.FromBMesh(tb)
    if at is None:
        at=me.attributes.new('eh_orig_z','FLOAT','POINT'); at.data.foreach_set('value',[-9999.0]*len(me.vertices))
    n=0
    for p in me.polygons:
        c=mw@p.center
        if not (min(xs)-4<c.x<max(xs)+4 and min(ys)-4<c.y<max(ys)+4): continue
        if fv.ray_cast(mathutils.Vector((c.x,c.y,c.z+5)),mathutils.Vector((0,0,-1)),10)[0] is not None: continue
        h=tv.ray_cast(mathutils.Vector((c.x,c.y,c.z+5)),mathutils.Vector((0,0,-1)))
        if h[0] is None: continue
        dz=h[0].z+0.01-c.z
        if dz>0.003:
            for vi in p.vertices:
                v=me.vertices[vi]; w=mw@v.co
                if at.data[vi].value<-9000: at.data[vi].value=w.z
                v.co=inv@mathutils.Vector((w.x,w.y,w.z+dz))
            n+=1
    me.update(); print('EH_LEAF faces',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('EH_SAVED')
