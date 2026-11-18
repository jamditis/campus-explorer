# Session eh (Oct 21 2026 ~9:45 PM ET): at the SW corner of the CCOM west forecourt the planar paving (eg) rides ~6 cm above the
# OSM footpath and ends in a jagged triangle across the walk (eyeW WIP). Tuck every forecourt vertex that lies over
# Footpaths_OSM to 3 cm below the path surface so the straight path edge becomes the clean border.
# Pre-tuck z in point attribute eh_orig_z. SAVE=1 saves; REVERT=1 restores.
import bpy, os, bmesh, mathutils
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE=os.environ.get('SAVE')=='1'
fc=bpy.data.objects['CCOM brick forecourt (ortho + photo)']; me=fc.data; mw=fc.matrix_world; inv=mw.inverted()
fp=bpy.data.objects['Footpaths_OSM']; dg=bpy.context.evaluated_depsgraph_get()
pb=bmesh.new(); pb.from_object(fp,dg); pb.transform(fp.matrix_world); pv=BVHTree.FromBMesh(pb)
at=me.attributes.get('eh_orig_z')
if REV:
    if at:
        for v,d in zip(me.vertices,at.data):
            if d.value>-9000: v.co.z=d.value
        me.attributes.remove(at)
    print('EH_TUCK_REVERT')
else:
    if at is None:
        at=me.attributes.new('eh_orig_z','FLOAT','POINT'); at.data.foreach_set('value',[-9999.0]*len(me.vertices))
    n=0
    for i,v in enumerate(me.vertices):
        w=mw@v.co
        h=pv.ray_cast(mathutils.Vector((w.x,w.y,w.z+2)),mathutils.Vector((0,0,-1)),5)
        if h[0] is None: continue
        zt=h[0].z-0.03
        if w.z>zt:
            if at.data[i].value<-9000: at.data[i].value=w.z
            v.co.z=(inv@mathutils.Vector((w.x,w.y,zt))).z; n+=1
    me.update(); print('EH_TUCK verts',n)
    sk=bpy.data.objects.get('CCOM forecourt edge skirt (ed)'); print('EH_SKIRT',bool(sk))
if SAVE: bpy.ops.wm.save_mainfile(); print('EH_SAVED')
