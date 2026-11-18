# ol cam (REVERT=1 removes): close-up of the new walk-edge curb over the ok lawn bank by the Schmitt entrance.
import bpy, os, sys
from mathutils import Vector
CN='OL_Schmitt_cams_20261031ol'; REV=os.environ.get('REVERT')=='1'; NAME='OL_CAM_closeup_schmitt_walk_curb_lawn_bank'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects): d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
if not REV:
    sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
    c=bpy.data.collections.new(CN); sc.collection.children.link(c)
    cu=bpy.data.objects['OL_Schmitt_entrance_walk_edge_curb']; me=cu.data
    t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mi=t.matrix_world.inverted()
    def gz(p):
        h,l,n,i=t.ray_cast(mi@Vector((p.x,p.y,400)),mi.to_3x3()@Vector((0,0,-1))); return (t.matrix_world@l).z if h else None
    E=Vector((10.6,141.1)); K=int(os.environ.get('K','0'))
    segs=[]
    for k in range(len(me.vertices)//8):
        v=[me.vertices[8*k+j].co for j in range(8)]
        top=(v[2]+v[6])/2; inn=(v[0]+v[4])/2; n=(top-inn); n.z=0; n.normalize(); g=gz(top)
        if g is None: continue
        d=(top.xy-E).length
        if 6<d<16: segs.append((top.z-g,k,top,n))
    segs.sort(key=lambda s:-s[0]); h,k,top,n=segs[min(K,len(segs)-1)]
    al=Vector((-n.y,n.x,0))
    loc=top-n*1.2+al*6.0; loc.z=top.z+1.6
    d=bpy.data.cameras.new(NAME); d.lens=30; d.clip_start=0.1; d.clip_end=3000
    ob=bpy.data.objects.new(NAME,d); c.objects.link(ob); ob.location=loc
    tgt=top+n*1.2-al*3.0+Vector((0,0,-0.6)); ob.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    v=tgt-loc; hh,l,nn,i,hob,m=sc.ray_cast(dg,loc,v.normalized(),distance=v.length)
    print('CAM',NAME,[round(x,2) for x in loc],'float',round(h,2),'first hit',hob.name if hh else None,round((l-loc).length,1) if hh else None,'of',round(v.length,1))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
