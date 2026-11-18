# om cam (REVERT=1 removes): close-up of a 1F Schmitt window near the entrance (sill drip grime, blind variation), K picks candidate.
import bpy, os, sys
from mathutils import Vector
CN='OM_Schmitt_cams_20261031om'; REV=os.environ.get('REVERT')=='1'; NAME='OM_CAM_closeup_schmitt_sill_drips_blinds'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects): d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
if not REV:
    sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
    c=bpy.data.collections.new(CN); sc.collection.children.link(c)
    me=bpy.data.objects['OM_Schmitt_sill_drip_grime'].data; E=Vector((10.6,141.1)); K=int(os.environ.get('K','0'))
    t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mi=t.matrix_world.inverted()
    cand=[]
    for p in me.polygons:
        cc=p.center; n=p.normal.copy(); n.z=0; n.normalize()
        h=sc.ray_cast(dg,cc+n*0.05,n,distance=0.4)[0]
        if h: n=-n
        hh,l,nn,i=t.ray_cast(mi@Vector((cc.x,cc.y,400)),mi.to_3x3()@Vector((0,0,-1)))
        g=(t.matrix_world@l).z if hh else cc.z-3
        d=(cc.xy-E).length
        if 8<d<34 and 2.8<cc.z-g<5.5: cand.append((d,cc,n,g))
    cand.sort(key=lambda x:x[0]); d,cc,n,g=cand[min(K,len(cand)-1)]
    al=Vector((-n.y,n.x,0))
    loc=cc+n*6.5+al*2.2; loc.z=cc.z+0.2
    cd=bpy.data.cameras.new(NAME); cd.lens=32; cd.clip_start=0.1; cd.clip_end=3000
    ob=bpy.data.objects.new(NAME,cd); c.objects.link(ob); ob.location=loc
    tgt=cc+Vector((0,0,0.35)); ob.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    v=tgt-loc; hh,l,nn,i,hob,m=sc.ray_cast(dg,loc,v.normalized(),distance=v.length)
    print('CAM',NAME,[round(x,2) for x in loc],'cands',len(cand),'first hit',hob.name if hh else None,round((l-loc).length,1) if hh else None,'of',round(v.length,1))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
