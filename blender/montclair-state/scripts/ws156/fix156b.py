# ws156b on ws156a: retire the stacked quoin/punch overlay boxes sitting proud of the lettering fin face (slide1096: letters on
# plain brick), re-seat the letters on the frontmost surface, and re-place the N-lawn eye cam by a clear-ray search (was inside a spruce).
import bpy, os, resource
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())
C=(W_N+W_S+E_N+E_S)/4; A=W_N; u=(E_N-W_N).normalized(); n=Vector((u.y,-u.x)); L=(E_N-W_N).length
if ((W_N+E_N)/2-C).dot(n)<0: n=-n
def sd(p): q=Vector((p.x,p.y)); return (q-A).dot(u),(q-A).dot(n)
fin=bpy.data.objects['UV_Freeman_N_lettering_brick_wing_UNVERIFIED']
FS=[sd(fin.matrix_world@v.co) for v in fin.data.vertices]; s0=min(s for s,_ in FS); s1=max(s for s,_ in FS); dfin=max(d for _,d in FS)
print('FIX156B fin s',round(s0,2),round(s1,2),'front d',round(dfin,3))
nret=0
for o in list(bpy.data.objects):
    if o.type!='MESH' or o.hide_render or o==fin or 'Freeman' not in o.name or o.name.startswith(('WS15','VT_')) or not o.data.vertices or len(o.data.polygons)>12: continue
    S=[sd(o.matrix_world@v.co) for v in o.data.vertices]; Z=[(o.matrix_world@v.co).z for v in o.data.vertices]
    if min(s for s,_ in S)>=s0-0.05 and max(s for s,_ in S)<=s1+0.05 and max(d for _,d in S)>dfin-0.01 and min(d for _,d in S)>-1.0 and max(Z)>129.5:
        o.hide_render=True; o.hide_viewport=True; o.name=o.name[:40]+'_RETIRED_ws156b'; nret+=1
print('FIX156B retired overlays on fin',nret)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
let=next(o for o in bpy.data.objects if o.type=='FONT' and 'FREEMAN' in o.data.body.upper())
mw=let.matrix_world.copy(); t=mw.translation.copy(); nl=mw.to_3x3()@Vector((0,0,1)); nl.z=0; nl.normalize(); ul=(mw.to_3x3()@Vector((1,0,0))); ul.z=0; ul.normalize()
let.hide_set(True); hide0=let.hide_render; let.hide_render=True; bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
best=None
for a in (-0.9,-0.45,0,0.45,0.9):
    for dz in (-0.2,0,0.2):
        o0=t+ul*a+Vector((0,0,dz))+nl*2.0
        ok,loc,nor,idx,ob,_=sc.ray_cast(dg,o0,-nl)
        if ok:
            dd=(loc-t).dot(nl); best=dd if best is None else max(best,dd)
            if dd>0.02: print('FIX156B proud hit',ob.name[:50],round(dd,3))
let.hide_render=hide0; let.hide_set(False)
if best is not None: mw.translation=t+nl*(best+let.data.extrude+0.006-0.0); let.matrix_world=mw
print('FIX156B letter shift',best and round(best,3))
# clear-ray eye cam on the N end from the N lawn
mid=(W_N+E_N)/2; T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
def gz(x,y,d):
    mi=T.matrix_world.inverted(); ok,loc,_,_=T.ray_cast(mi@Vector((x,y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@loc).z if ok else d
tg=[Vector(((W_N+u*(L*f)).x,(W_N+u*(L*f)).y,z)) for f in (0.15,0.5,0.85) for z in (131.0,137.0,143.0)]
cands=[]
for dist in (18,22,26,30,36,42):
    for lat in (-12,-8,-4,0,4,8,12):
        p=mid+n*dist+u*lat; pos=Vector((p.x,p.y,gz(p.x,p.y,128.5)+1.6)); hit=0
        for q in tg:
            v=q-pos; ok,loc,nor,idx,ob,_=sc.ray_cast(dg,pos,v.normalized(),distance=v.length+1.0)
            if ok and 'Freeman' in ob.name and (loc-pos).length>v.length-2.0: hit+=1
        cands.append((hit,-abs(lat),-dist,pos))
cands.sort(key=lambda x:(x[0],x[1],x[2]),reverse=True); h,_,_,pos=cands[0]
print('FIX156B lawn cam hits',h,'/',len(tg),tuple(round(x,1) for x in pos))
c=bpy.data.objects['WS156_CAM_eye_Freeman_N_end_from_N_lawn']; c.location=pos; c.rotation_euler=(Vector((mid.x,mid.y,137.0))-pos).to_track_quat('-Z','Y').to_euler(); c.data.lens=24
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws156b.blend',copy=True)
print('SAVED_WS156B RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
