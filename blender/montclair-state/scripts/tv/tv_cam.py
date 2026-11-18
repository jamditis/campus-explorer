# tv: permanent eye-level camera on Blanton door 1 (tu checked it numerically only). REVERT=1 removes it.
import bpy, os, json
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'; REV=os.environ.get('REVERT')=='1'
N='TV_CAM_eye_Blanton_door1'
if REV:
    o=bpy.data.objects.get(N)
    if o: bpy.data.objects.remove(o)
else:
    G=bpy.data.objects['TJ_Blanton_entrance_1_glass_UNVERIFIED']
    gv=[G.matrix_world@v.co for v in G.data.vertices]; c=sum(gv,Vector())/len(gv)
    zmin=min(v.z for v in gv)
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    best=None
    for s in (1,-1):
        n=Vector((-0.40263208746910095*s,-0.9153618812561035*s,0))
        for d in (11,9,7,5):
            for side in (0,2.5,-2.5):
                u=Vector((-n.y,n.x,0))
                loc=c+n*d+u*side; loc.z=zmin+1.65
                # down ray for ground
                hit,p,_,_,ob,_=sc.ray_cast(dg,loc+Vector((0,0,30)),Vector((0,0,-1)))
                if hit: loc.z=p.z+1.65
                tgt=c+Vector((0,0,0.3))
                dirv=(tgt-loc); dist=dirv.length; dirv.normalize()
                hit2,p2,_,_,ob2,_=sc.ray_cast(dg,loc,dirv,distance=dist-0.3)
                ok=not hit2
                print('TRY',s,d,side,ok,ob2.name if hit2 else '-',ob.name if hit else '-')
                if ok and best is None: best=(loc.copy(),tgt)
    if best is None: raise SystemExit('NO CLEAR VIEW')
    loc,tgt=best
    o=bpy.data.objects.get(N)
    if not o:
        cd=bpy.data.cameras.new(N); cd.lens=28
        o=bpy.data.objects.new(N,cd)
        col=bpy.data.collections.get('TU_blanton_entry_fix_UNVERIFIED') or sc.collection
        col.objects.link(o)
    o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    print('CAM',tuple(loc),tuple(tgt))
if SAVE: bpy.ops.wm.save_mainfile()
