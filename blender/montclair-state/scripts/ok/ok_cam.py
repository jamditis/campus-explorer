# ok cams (REVERT=1 removes): close-up of the +a (NNE) pavilion return plinth/cap + wing windows; eye view of the WNW long
# facade from close in, oblique from the SSW (og WNW cam is mostly trees).
import bpy, os, sys
from mathutils import Vector
CN='OK_Schmitt_cams_20261031ok'; REV=os.environ.get('REVERT')=='1'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects): d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
if not REV:
    c=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(c)
    sc=bpy.context.scene; bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
    fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
    cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb); cen.z=0
    OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0))
    def P(a,o,z): return cen+AL*a+OUT*o+Vector((0,0,z))
    t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mi=t.matrix_world.inverted()
    def gz(p):
        h,l,n,i=t.ray_cast(mi@Vector((p.x,p.y,400)),mi.to_3x3()@Vector((0,0,-1))); return (t.matrix_world@l).z if h else 138
    def cam(name,loc,tgt,lens):
        d=bpy.data.cameras.new(name); d.lens=lens; d.clip_start=0.1; d.clip_end=3000
        ob=bpy.data.objects.new(name,d); c.objects.link(ob); ob.location=loc
        ob.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
        v=tgt-loc; h,l,n,i,hob,m=sc.ray_cast(dg,loc,v.normalized(),distance=v.length)
        print('CAM',name,[round(x,2) for x in loc],'first hit',hob.name if h else None, round((l-loc).length,1) if h else None,'of',round(v.length,1))
    A=float(os.environ.get('CA','8.6')); O=float(os.environ.get('CO','3.2'))
    cam('OK_CAM_closeup_schmitt_return_plinth_wing_windows',P(A,O,gz(P(A,O,0))+1.45),P(4.6,-3.6,140.2),28)
    ws=[o for o in bpy.data.objects if o.name.startswith('SCH_win_') and o.get('run')=='(-0.92, 0.4, 77)' and o.get('row')==1]
    ctr=sum((o.matrix_world.translation for o in ws),Vector())/len(ws)
    M=ws[0].matrix_world; X=(M.to_3x3()@Vector((1,0,0))).normalized(); Y=(M.to_3x3()@Vector((0,1,0))).normalized()
    D=float(os.environ.get('WD','14')); S=float(os.environ.get('WS','-24'))
    q=ctr+Y*D+X*S; q.z=gz(q)+1.65
    cam('OK_CAM_eye_schmitt_WNW_facade_close',q,ctr+X*float(os.environ.get('WT','1'))+Vector((0,0,0.5)),24)
    # NNE end-facade cam dropped: that end faces CCIS at close range (camera ended up inside CCIS walls)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
