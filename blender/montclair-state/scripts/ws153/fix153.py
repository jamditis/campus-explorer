# ws153: UNIFY #57 finish (old Freeman W/E skins lose faces in front of the WS152 overlay; close-up cam clear of trees) + #58 residual tone.
import bpy, bmesh, resource
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())   # defines W_N,W_S,E_N,E_S (wall offset measured 0.0 in ws152f)
KEYS=('skin','pane','glass','tint','grid','backplane','frame','mullion','window','slot','sash')
NAMES=['UY_Freeman_W_cream_brick_skin','VD_Freeman_W_pane_grid','VF_Freeman_W_sky_tint_continuous','VC_Freeman_W_glass_backplanes',
       'VC_Freeman_E_glass_backplanes','VG_Freeman_E_glass_backplanes','VG_Freeman_E_pane_grid']
planes=[]
for N,S,sg in [(W_N,W_S,1),(E_N,E_S,-1)]:
    u=(S-N).normalized(); n=Vector((u.y,-u.x))*sg; planes.append((N,u,n,(S-N).length))
def near(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    for N,u,n,L in planes:
        if max((p.xy-N).dot(n) for p in bb)>-0.2 and min((p.xy-N).dot(n) for p in bb)<0.6 and max(p.z for p in bb)>129: return True
    return False
cands=[o for o in bpy.data.objects if o.type=='MESH' and 'freeman' in o.name.lower() and not o.name.startswith('WS152')
       and '_RETIRED' not in o.name and not o.hide_render and (any(o.name.startswith(k) for k in NAMES) or (any(k in o.name.lower() for k in KEYS) and near(o)))]
print('FIX153 candidates',len(cands),[o.name for o in cands])
tot=0
for o in cands:
    me=o.data
    if me.users>1: o.data=me=me.copy()
    bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world; r3=mw.to_3x3()
    dl=[]
    for f in bm.faces:
        c=mw@f.calc_center_median(); nw=(r3@f.normal).normalized()
        for N,u,n,L in planes:
            d=(c.xy-N).dot(n); s=(c.xy-N).dot(u)
            if -0.2<=d<=0.6 and -0.3<=s<=L+0.3 and c.z>127.5:   # all faces in the band (pane-grid fin sides protrude 0.35 m)
                dl.append(f); break
    nf=len(bm.faces); bmesh.ops.delete(bm,geom=dl,context='FACES'); left=len(bm.faces); bm.to_mesh(me); bm.free(); me.update()
    tot+=len(dl); print('FIX153 faces',o.name,nf,'->',left)
    if left==0: o.hide_render=True; o.hide_viewport=True; o.name=o.name[:40]+'_RETIRED_ws153'
print('FIX153 deleted faces',tot)
# --- close-up camera: search a spot with a clear line of sight to the W overlay (scene ray casts, evaluated trees)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
N,u,n,L=planes[0]; T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
def gz(x,y,d):
    if not T: return d
    mi=T.matrix_world.inverted(); ok,loc,_,_=T.ray_cast(mi@Vector((x,y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@loc).z if ok else d
best=None
for so in [L*0.5+k for k in (2,4,6,8,10,-2,-4,-6,-8,0,12,14)]:
    for dist in (8,10,12,7):
        p2=N+u*so+n*dist; pos=Vector((p2.x,p2.y,gz(p2.x,p2.y,127.8)+1.6))
        tg=N+u*(so+3)
        clear=0; tests=0
        for ds in (-2.5,0,2.5,5,7.5):
            for z in (130.5,133.5,137.0):
                t=Vector(((N+u*(so+ds)).x,(N+u*(so+ds)).y,z)); v=t-pos; tests+=1
                ok,loc,nor,idx,ob,_=sc.ray_cast(dg,pos,v.normalized(),distance=v.length+0.6)
                if ok and (ob.name.startswith('WS152') or 'Freeman Hall walls' in ob.name) : clear+=1
        sco=(clear,-abs(so-L*0.5-4),-abs(dist-9))
        if best is None or sco>best[0]: best=(sco,pos,Vector((tg.x,tg.y,133.5)),so,dist)
        if clear==tests: break
    if best and best[0][0]==15: break
print('FIX153 cam',best[0],'s',round(best[3],2),'dist',best[4],tuple(round(x,2) for x in best[1]))
c=bpy.data.objects['WS152_CAM_closeup_Freeman_W_bay']; c.data.lens=28; c.location=best[1]
c.rotation_euler=(best[2]-best[1]).to_track_quat('-Z','Y').to_euler()
# --- #58 residual: seam strips + N triangle take the lot's asphalt material
mats={}
for o in bpy.data.objects:
    if o.type=='MESH' and 'lot9' in o.name.lower().replace('_','') and o.active_material: mats.setdefault(o.active_material.name,[]).append(o.name[:60])
for k,v in mats.items(): print('FIX153 lot9 mat',k,len(v),v[:4])
lot=[o for o in bpy.data.objects if o.name.startswith('WS142_Lot9') and 'asphalt' in o.name.lower() and o.active_material]
if lot:
    lm=lot[0].active_material; print('FIX153 lot material',lot[0].name,lm.name)
    for o in bpy.data.objects:
        if o.type=='MESH' and (o.name.startswith('WS152_Lot9_Skyline_junction_seam') or o.name.startswith('WS152_Lot9_S_patch_seam')):
            o.data.materials.clear(); o.data.materials.append(lm); print('FIX153 retoned',o.name)
bpy.ops.wm.save_as_mainfile(filepath=__import__('os').environ.get('OUT153',M+'montclair_state_ws153a.blend'),copy=True)
print('SAVED_WS153A RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
