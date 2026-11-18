import bpy, math, sys
from mathutils import Vector
sc=bpy.context.scene; DG=bpy.context.evaluated_depsgraph_get()
col=bpy.data.collections.get('OG_Schmitt_Hall_windows_modelled_20261031og')
C=Vector((-3.4,153.4,0)); u=Vector((math.cos(math.radians(66.7)),math.sin(math.radians(66.7)),0)); n1=Vector((u.y,-u.x,0))
def rc(o,d,dist=1e4):
    t=0.0
    while t<dist:
        h,l,nn,i,ob,_=sc.ray_cast(DG,o+d*t,d,distance=dist-t)
        if not h: return False,None,None,None
        if ob.name.startswith('T_') or 'tree' in ob.name.lower() or ob.name.startswith('CCOM_Win') or ob.name.startswith('SCH_win'):
            t+=(l-(o+d*t)).length+0.05; 
            if ob.name.startswith('CCOM_Win') or ob.name.startswith('SCH_win'): return True,l,nn,ob
            continue
        return True,l,nn,ob
    return False,None,None,None
def gz(p):
    h,l,_,_=rc(Vector((p.x,p.y,300)),Vector((0,0,-1)))
    return l.z if h else 138.4
def wallpt(n,s,z):
    o=C+u*s+n*40; o.z=z
    h,l,nn,ob=rc(o,-n,60); return l if h else None, ob.name if h else None
CAMS={}
def cam(name,pos,tgt,lens):
    cd=bpy.data.cameras.get(name) or bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=3000
    ob=bpy.data.objects.get(name) or bpy.data.objects.new(name,cd)
    if ob.name not in col.objects: col.objects.link(ob)
    ob.location=pos; ob.rotation_euler=(tgt-pos).to_track_quat('-Z','Y').to_euler()
    d=(tgt-pos); h,l,nn,i,obh,_=sc.ray_cast(DG,pos,d.normalized(),distance=d.length+5)
    print('CAM',name,tuple(round(x,1) for x in pos),'first hit',obh.name if h else None, round((l-pos).length,1) if h else None)
for nm,n,s in (('ESE',n1,-6),('WNW',-n1,8)):
    w,ob=wallpt(n,s,143); print('wall',nm,w,ob)
    CAMS[nm]=(w,n)
w,n=CAMS['ESE']; p=w+n*26-u*9; p.z=gz(p)+1.7; cam('OG_CAM_eye_schmitt_ESE_long_facade',p,w+u*4+Vector((0,0,0.5)),24)
w,n=CAMS['WNW']; p=w+n*26+u*9; p.z=gz(p)+1.7; cam('OG_CAM_eye_schmitt_WNW_long_facade',p,w-u*4+Vector((0,0,0.5)),24)
w,n=CAMS['ESE']; p=w+n*8+u*1.5; p.z=gz(p)+3.2; cam('OG_CAM_closeup_schmitt_ESE_windows',p,w-u*2+Vector((0,0,0.8)),35)
p=C+n1*75-u*55; p.z=205; cam('OG_CAM_oblique_schmitt_from_SE',p,C+Vector((0,0,144)),35)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
# og pass 2: entrance close-up + N-end eye view (lower storey on the slope)
import json as _j
stt = _j.loads(bpy.data.objects['Schmitt Hall walls'].get('og_build_state', '{}'))
if stt:
    Nn = Vector((0.92, -0.40, 0)).normalized(); Xx = Vector((0, 0, 1)).cross(Nn)
    W0 = Vector((stt['wall'][0], stt['wall'][1], 0)); G = stt['grade']
    p = W0 + Nn * 6.5 - Xx * 3.0; p.z = G + 1.65
    cam('OG_CAM_closeup_schmitt_E_entrance_door', p, W0 + Vector((0, 0, G + 1.6)), 28)
nn = Vector((0.39, 0.92, 0)).normalized()
w, ob = wallpt(nn, 38, 140.5); print('N end wall', w, ob)
if w is not None:
    p = w + nn * 24 + Vector((nn.y, -nn.x, 0)) * 10; p.z = gz(p) + 1.7
    cam('OG_CAM_eye_schmitt_N_end_lower_storey', p, w + Vector((0, 0, -0.5)), 24)
if '--save2' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED2')
